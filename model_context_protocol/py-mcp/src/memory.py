"""
FastMCP Server with Memory Optimization using PostgreSQL pgvector

A recursive memory system inspired by human brain clustering, using:
- OpenAI's text-embedding-3-small for semantic understanding
- PostgreSQL pgvector for efficient similarity search
- Pydantic-AI for LLM integration
"""

import asyncio
import logging
import math
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Self, TypeVar

import asyncpg
import numpy as np
from openai import AsyncOpenAI
from pgvector.asyncpg import register_vector
from pydantic import BaseModel, Field
from pydantic_ai import Agent

from mcp.server.fastmcp import FastMCP

# Configuration
MAX_DEPTH = 5
SIMILARITY_THRESHOLD = 0.7
DECAY_FACTOR = 0.99
REINFORCEMENT_FACTOR = 1.1

DEFAULT_LLM_MODEL = "openai:gpt-4o"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"

T = TypeVar("T")

# FastMCP server instance
mcp = FastMCP(
    "memory",
    dependencies=[
        "pydantic-ai-slim[openai]",
        "asyncpg",
        "numpy",
        "pgvector",
    ],
)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_DSN = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:54320/memory_db"
)

# Profile directory for persistent storage
PROFILE_DIR = (
    Path.home() / ".fastmcp" / os.environ.get("USER", "anon") / "memory"
).resolve()
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

logger.info(f"Database DSN: {DB_DSN}")
logger.info(f"Profile directory: {PROFILE_DIR}")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate cosine similarity between two embedding vectors."""
    a_array = np.array(a, dtype=np.float64)
    b_array = np.array(b, dtype=np.float64)
    dot_product = np.dot(a_array, b_array)
    norm_a = np.linalg.norm(a_array)
    norm_b = np.linalg.norm(b_array)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


async def do_ai(
    user_prompt: str,
    system_prompt: str,
    result_type: type[T] | Annotated,
    deps=None,
) -> T:
    """Execute LLM call with Pydantic-AI for structured output."""
    agent = Agent(
        DEFAULT_LLM_MODEL,
        system_prompt=system_prompt,
        result_type=result_type,
    )
    result = await agent.run(user_prompt, deps=deps)
    return result.data


# ============================================================================
# DEPENDENCIES DATACLASS
# ============================================================================

@dataclass
class Deps:
    """Dependency injection container for AsyncOpenAI and database pool."""
    openai: AsyncOpenAI
    pool: asyncpg.Pool


# ============================================================================
# DATABASE SETUP
# ============================================================================

async def get_db_pool() -> asyncpg.Pool:
    """Create and configure asyncpg connection pool with pgvector support."""
    async def init(conn):
        """Initialize connection with pgvector extension."""
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        await register_vector(conn)

    pool = await asyncpg.create_pool(DB_DSN, init=init)
    logger.info("Database pool created")
    return pool


# ============================================================================
# DATA MODELS
# ============================================================================

class MemoryNode(BaseModel):
    """Represents a stored memory with semantic embedding and metadata."""
    id: int | None = None
    content: str
    summary: str = ""
    importance: float = 1.0
    access_count: int = 0
    timestamp: float = Field(
        default_factory=lambda: datetime.now(timezone.utc).timestamp()
    )
    embedding: list[float]

    @classmethod
    async def from_content(cls, content: str, deps: Deps):
        """Create MemoryNode from text by generating embedding."""
        embedding = await get_embedding(content, deps)
        return cls(content=content, embedding=embedding)

    async def save(self, deps: Deps):
        """Save or update memory in database."""
        async with deps.pool.acquire() as conn:
            if self.id is None:
                # Insert new memory
                result = await conn.fetchrow(
                    """
                    INSERT INTO memories (content, summary, importance, access_count,
                        timestamp, embedding)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id
                    """,
                    self.content,
                    self.summary,
                    self.importance,
                    self.access_count,
                    self.timestamp,
                    self.embedding,
                )
                self.id = result["id"]
                logger.info(f"Saved new memory: {self.id}")
            else:
                # Update existing memory
                await conn.execute(
                    """
                    UPDATE memories
                    SET content = $1, summary = $2, importance = $3,
                        access_count = $4, timestamp = $5, embedding = $6
                    WHERE id = $7
                    """,
                    self.content,
                    self.summary,
                    self.importance,
                    self.access_count,
                    self.timestamp,
                    self.embedding,
                    self.id,
                )
                logger.info(f"Updated memory: {self.id}")

    async def merge_with(self, other: Self, deps: Deps):
        """Merge similar memory into this one."""
        logger.info(f"Merging memory {other.id} into {self.id}")

        # Combine content
        combined_content = f"{self.content}\n\n{other.content}"
        self.content = await do_ai(
            combined_content,
            "Combine the following two texts into a single, coherent text.",
            str,
            deps,
        )

        # Update metadata
        self.importance += other.importance
        self.access_count += other.access_count
        self.embedding = [
            (a + b) / 2 for a, b in zip(self.embedding, other.embedding)
        ]

        # Generate summary
        self.summary = await do_ai(
            self.content,
            "Summarize the following text concisely in 1-2 sentences.",
            str,
            deps,
        )

        # Save merged memory
        await self.save(deps)

        # Delete the merged node
        if other.id is not None:
            await delete_memory(other.id, deps)

    def get_effective_importance(self) -> float:
        """Calculate effective importance with access count factor."""
        return self.importance * (1 + math.log(self.access_count + 1))


# ============================================================================
# EMBEDDING & AI OPERATIONS
# ============================================================================

async def get_embedding(text: str, deps: Deps) -> list[float]:
    """Generate embedding vector for text using OpenAI."""
    logger.debug(f"Generating embedding for: {text[:50]}...")
    embedding_response = await deps.openai.embeddings.create(
        input=text,
        model=DEFAULT_EMBEDDING_MODEL,
    )
    return embedding_response.data[0].embedding


# ============================================================================
# MEMORY MANAGEMENT OPERATIONS
# ============================================================================

async def delete_memory(memory_id: int, deps: Deps):
    """Delete memory by ID from database."""
    async with deps.pool.acquire() as conn:
        await conn.execute("DELETE FROM memories WHERE id = $1", memory_id)
    logger.info(f"Deleted memory: {memory_id}")


async def add_memory(content: str, deps: Deps):
    """Add new memory with automatic clustering of similar memories."""
    logger.info(f"Adding memory: {content[:50]}...")

    # Create and save new memory
    new_memory = await MemoryNode.from_content(content, deps)
    await new_memory.save(deps)

    # Find and merge similar memories
    similar_memories = await find_similar_memories(new_memory.embedding, deps)
    for memory in similar_memories:
        if memory.id != new_memory.id:
            similarity = cosine_similarity(
                new_memory.embedding, memory.embedding
            )
            if similarity > SIMILARITY_THRESHOLD:
                logger.info(
                    f"Merging similar memory (similarity: {similarity:.2f})"
                )
                await new_memory.merge_with(memory, deps)

    # Update importance scores
    await update_importance(new_memory.embedding, deps)

    # Prune old memories if exceeding MAX_DEPTH
    await prune_memories(deps)

    result = f"Remembered: {content}"
    logger.info(result)
    return result


async def find_similar_memories(
    embedding: list[float], deps: Deps
) -> list[MemoryNode]:
    """Find similar memories using pgvector similarity search."""
    async with deps.pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, content, summary, importance, access_count, timestamp, embedding
            FROM memories
            ORDER BY embedding <-> $1
            LIMIT 5
            """,
            embedding,
        )

    memories = [
        MemoryNode(
            id=row["id"],
            content=row["content"],
            summary=row["summary"],
            importance=row["importance"],
            access_count=row["access_count"],
            timestamp=row["timestamp"],
            embedding=row["embedding"],
        )
        for row in rows
    ]
    logger.debug(f"Found {len(memories)} similar memories")
    return memories


async def update_importance(user_embedding: list[float], deps: Deps):
    """Update importance scores based on semantic similarity."""
    async with deps.pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, importance, access_count, embedding FROM memories"
        )

        for row in rows:
            memory_embedding = row["embedding"]
            similarity = cosine_similarity(user_embedding, memory_embedding)

            if similarity > SIMILARITY_THRESHOLD:
                new_importance = row["importance"] * REINFORCEMENT_FACTOR
                new_access_count = row["access_count"] + 1
            else:
                new_importance = row["importance"] * DECAY_FACTOR
                new_access_count = row["access_count"]

            await conn.execute(
                """
                UPDATE memories
                SET importance = $1, access_count = $2
                WHERE id = $3
                """,
                new_importance,
                new_access_count,
                row["id"],
            )

    logger.debug("Updated importance scores")


async def prune_memories(deps: Deps):
    """Remove oldest or least important memories if exceeding MAX_DEPTH."""
    async with deps.pool.acquire() as conn:
        # Get memory count
        count_result = await conn.fetchval("SELECT COUNT(*) FROM memories")
        if count_result > MAX_DEPTH:
            logger.info(f"Pruning memories (count: {count_result} > {MAX_DEPTH})")
            rows = await conn.fetch(
                """
                SELECT id, importance, access_count
                FROM memories
                ORDER BY importance DESC
                OFFSET $1
                """,
                MAX_DEPTH,
            )
            for row in rows:
                await conn.execute("DELETE FROM memories WHERE id = $1", row["id"])
            logger.info(f"Pruned {len(rows)} memories")


async def display_memory_tree(deps: Deps) -> str:
    """Display memory tree as formatted string for user."""
    async with deps.pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT content, summary, importance, access_count
            FROM memories
            ORDER BY importance DESC
            LIMIT $1
            """,
            MAX_DEPTH,
        )

    result = "## Memory Profile\n\n"
    if not rows:
        result += "*(No memories stored yet)*"
        return result

    for idx, row in enumerate(rows, 1):
        effective_importance = row["importance"] * (
            1 + math.log(row["access_count"] + 1)
        )
        summary = row["summary"] or row["content"][:100]
        result += (
            f"{idx}. {summary}\n"
            f"   Importance: {effective_importance:.2f} | "
            f"Access: {row['access_count']}\n\n"
        )

    return result


# ============================================================================
# MCP TOOLS (Exported via MCP Protocol)
# ============================================================================

@mcp.tool()
async def remember(
    contents: list[str] = Field(
        description="List of observations or memories to store"
    ),
) -> str:
    """Store new memories and automatically cluster similar ones.

    This tool accepts a list of memory texts, generates embeddings,
    stores them in the vector database, and automatically merges
    similar memories to maintain an organized knowledge base.

    Args:
        contents: List of memory strings to store

    Returns:
        Confirmation message with stored content summary
    """
    deps = Deps(openai=AsyncOpenAI(), pool=await get_db_pool())
    try:
        logger.info(f"Remember tool called with {len(contents)} items")
        results = await asyncio.gather(
            *[add_memory(content, deps) for content in contents]
        )
        return "\n".join(results)
    except Exception as e:
        logger.error(f"Error in remember tool: {e}", exc_info=True)
        raise
    finally:
        await deps.pool.close()


@mcp.tool()
async def read_profile() -> str:
    """Retrieve and display the current memory profile.

    This tool returns the user's memory tree sorted by importance,
    showing the top memories with their access counts and scores.

    Returns:
        Formatted string with memory tree and metadata
    """
    deps = Deps(openai=AsyncOpenAI(), pool=await get_db_pool())
    try:
        logger.info("Read profile tool called")
        profile = await display_memory_tree(deps)
        return profile
    except Exception as e:
        logger.error(f"Error in read_profile tool: {e}", exc_info=True)
        raise
    finally:
        await deps.pool.close()


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

async def initialize_database():
    """Initialize PostgreSQL database with pgvector extension and schema."""
    logger.info("Initializing database...")

    # Connect to default postgres database
    pool = await asyncpg.create_pool(
        "postgresql://postgres:postgres@localhost:54320/postgres"
    )
    try:
        async with pool.acquire() as conn:
            # Terminate existing connections to memory_db
            await conn.execute(
                """
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = 'memory_db'
                AND pid <> pg_backend_pid();
                """
            )
            logger.info("Terminated existing connections")

            # Drop and recreate database
            await conn.execute("DROP DATABASE IF EXISTS memory_db;")
            await conn.execute("CREATE DATABASE memory_db;")
            logger.info("Created memory_db database")
    finally:
        await pool.close()

    # Connect to memory_db and initialize schema
    pool = await asyncpg.create_pool(DB_DSN)
    try:
        async with pool.acquire() as conn:
            # Enable pgvector
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            await register_vector(conn)
            logger.info("Enabled pgvector extension")

            # Create memories table
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    summary TEXT,
                    importance REAL NOT NULL DEFAULT 1.0,
                    access_count INT NOT NULL DEFAULT 0,
                    timestamp DOUBLE PRECISION NOT NULL,
                    embedding vector(1536) NOT NULL
                );
                """
            )
            logger.info("Created memories table")

            # Create vector index for efficient similarity search
            await conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_memories_embedding ON memories
                    USING hnsw (embedding vector_l2_ops);
                """
            )
            logger.info("Created pgvector HNSW index")
    finally:
        await pool.close()

    logger.info("Database initialization complete")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "init":
        # Initialize database: python -m src.memory init
        asyncio.run(initialize_database())
    else:
        # Run FastMCP server
        logger.info("Starting FastMCP Memory Server...")
        mcp.run()
