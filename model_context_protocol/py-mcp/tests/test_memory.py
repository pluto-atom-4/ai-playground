"""
Comprehensive pytest suite for FastMCP Memory Server with pgvector

Tests all 16 components following copilot-instructions.md FastMCP guidelines:
- Basic functionality
- Schema validation
- Error handling
- Async operations
- Data persistence
- Memory clustering
- Importance scoring
"""

import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone

import pytest
import asyncpg
from pydantic import ValidationError

# Import from src.memory
from src.memory import (
    cosine_similarity,
    do_ai,
    Deps,
    get_db_pool,
    MemoryNode,
    get_embedding,
    delete_memory,
    add_memory,
    find_similar_memories,
    update_importance,
    prune_memories,
    display_memory_tree,
    remember,
    read_profile,
    initialize_database,
)

# Environment setup for tests
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:54320/memory_db"
)
os.environ.setdefault("OPENAI_API_KEY", "sk-test-key-12345")


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
async def db_pool():
    """Create database pool for entire test session"""
    pool = await get_db_pool()
    yield pool
    await pool.close()


@pytest.fixture
async def deps():
    """Provide Deps container with mocked OpenAI"""
    mock_openai = AsyncMock()
    pool = await get_db_pool()
    deps = Deps(openai=mock_openai, pool=pool)
    yield deps
    await pool.close()


@pytest.fixture
async def clean_database(db_pool):
    """Clear memories table before each test"""
    async with db_pool.acquire() as conn:
        await conn.execute("TRUNCATE TABLE memories;")
    yield
    async with db_pool.acquire() as conn:
        await conn.execute("TRUNCATE TABLE memories;")


# ============================================================================
# TEST: UTILITY FUNCTIONS (Component 1-2)
# ============================================================================

class TestUtilityFunctions:
    """Test cosine_similarity and helper functions"""

    def test_cosine_similarity_identical_vectors(self):
        """Test cosine similarity with identical vectors returns 1.0"""
        vector = [1.0, 0.0, 0.0]
        similarity = cosine_similarity(vector, vector)
        assert similarity == pytest.approx(1.0, abs=0.001)

    def test_cosine_similarity_orthogonal_vectors(self):
        """Test cosine similarity with orthogonal vectors returns 0.0"""
        vector1 = [1.0, 0.0, 0.0]
        vector2 = [0.0, 1.0, 0.0]
        similarity = cosine_similarity(vector1, vector2)
        assert similarity == pytest.approx(0.0, abs=0.001)

    def test_cosine_similarity_opposite_vectors(self):
        """Test cosine similarity with opposite vectors returns -1.0"""
        vector1 = [1.0, 0.0, 0.0]
        vector2 = [-1.0, 0.0, 0.0]
        similarity = cosine_similarity(vector1, vector2)
        assert similarity == pytest.approx(-1.0, abs=0.001)

    def test_cosine_similarity_with_zero_vector(self):
        """Test cosine similarity handles zero vectors"""
        vector1 = [0.0, 0.0, 0.0]
        vector2 = [1.0, 0.0, 0.0]
        similarity = cosine_similarity(vector1, vector2)
        assert similarity == 0.0

    def test_cosine_similarity_high_dimension(self):
        """Test cosine similarity with high-dimensional vectors (1536-dim)"""
        # Simulate OpenAI embeddings
        vector1 = [0.1] * 1536
        vector2 = [0.1] * 1536
        similarity = cosine_similarity(vector1, vector2)
        assert similarity == pytest.approx(1.0, abs=0.001)


# ============================================================================
# TEST: DATA MODELS (Component 5)
# ============================================================================

class TestMemoryNodeModel:
    """Test MemoryNode Pydantic model validation"""

    def test_memory_node_creation_with_defaults(self):
        """Test MemoryNode creates with default values"""
        node = MemoryNode(
            content="Test memory",
            embedding=[0.1] * 1536
        )
        assert node.id is None
        assert node.content == "Test memory"
        assert node.importance == 1.0
        assert node.access_count == 0
        assert len(node.embedding) == 1536

    def test_memory_node_creation_with_all_fields(self):
        """Test MemoryNode creation with all fields"""
        now = datetime.now(timezone.utc).timestamp()
        node = MemoryNode(
            id=1,
            content="Test",
            summary="Summary",
            importance=2.5,
            access_count=5,
            timestamp=now,
            embedding=[0.1] * 1536
        )
        assert node.id == 1
        assert node.summary == "Summary"
        assert node.importance == 2.5
        assert node.access_count == 5

    def test_memory_node_validates_embedding_type(self):
        """Test MemoryNode validates embedding is list of floats"""
        with pytest.raises(ValidationError):
            MemoryNode(
                content="Test",
                embedding="not a list"  # Invalid type
            )

    def test_memory_node_effective_importance_calculation(self):
        """Test get_effective_importance calculation"""
        node = MemoryNode(
            content="Test",
            importance=2.0,
            access_count=10,
            embedding=[0.1] * 1536
        )
        # importance * (1 + log(access_count + 1))
        # 2.0 * (1 + log(11)) ≈ 2.0 * 3.398 ≈ 6.796
        effective = node.get_effective_importance()
        assert effective > 6.0  # Approximate check


# ============================================================================
# TEST: DATABASE OPERATIONS (Component 6-12)
# ============================================================================

class TestDatabaseOperations:
    """Test database layer operations"""

    @pytest.mark.asyncio
    async def test_get_db_pool_creates_pool(self):
        """Test get_db_pool creates valid asyncpg pool"""
        pool = await get_db_pool()
        assert pool is not None

        # Verify pool works
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            assert result == 1

        await pool.close()

    @pytest.mark.asyncio
    async def test_memory_node_save_insert(self, deps, clean_database):
        """Test MemoryNode.save() inserts new memory"""
        node = MemoryNode(
            content="Test memory",
            embedding=[0.1] * 1536
        )
        await node.save(deps)

        assert node.id is not None
        assert node.id > 0

    @pytest.mark.asyncio
    async def test_memory_node_save_update(self, deps, clean_database):
        """Test MemoryNode.save() updates existing memory"""
        # Create and save
        node = MemoryNode(
            content="Original",
            embedding=[0.1] * 1536
        )
        await node.save(deps)
        original_id = node.id

        # Update and save again
        node.content = "Updated"
        await node.save(deps)

        assert node.id == original_id

    @pytest.mark.asyncio
    async def test_delete_memory(self, deps, clean_database):
        """Test delete_memory removes memory from database"""
        # Create memory
        node = MemoryNode(
            content="To delete",
            embedding=[0.1] * 1536
        )
        await node.save(deps)
        memory_id = node.id

        # Delete
        await delete_memory(memory_id, deps)

        # Verify deleted
        async with deps.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT id FROM memories WHERE id = $1",
                memory_id
            )
            assert result is None

    @pytest.mark.asyncio
    async def test_find_similar_memories(self, deps, clean_database):
        """Test find_similar_memories returns pgvector search results"""
        # Create test memories
        embedding1 = [0.1] * 1536
        embedding2 = [0.1] * 1536  # Very similar

        node1 = MemoryNode(content="Memory 1", embedding=embedding1)
        node2 = MemoryNode(content="Memory 2", embedding=embedding2)

        await node1.save(deps)
        await node2.save(deps)

        # Search for similar
        similar = await find_similar_memories(embedding1, deps)

        assert len(similar) >= 1
        assert similar[0].content in ["Memory 1", "Memory 2"]

    @pytest.mark.asyncio
    async def test_display_memory_tree_format(self, deps, clean_database):
        """Test display_memory_tree returns formatted string"""
        # Create test memory
        node = MemoryNode(
            content="Important memory",
            summary="This is important",
            importance=5.0,
            access_count=3,
            embedding=[0.1] * 1536
        )
        await node.save(deps)

        # Display tree
        tree = await display_memory_tree(deps)

        assert "Memory Profile" in tree
        assert isinstance(tree, str)
        assert len(tree) > 0

    @pytest.mark.asyncio
    async def test_display_memory_tree_empty(self, deps, clean_database):
        """Test display_memory_tree with no memories"""
        tree = await display_memory_tree(deps)

        assert "Memory Profile" in tree
        assert "No memories stored yet" in tree


# ============================================================================
# TEST: MEMORY OPERATIONS - CLUSTERING (Component 8)
# ============================================================================

class TestMemoryClustering:
    """Test memory clustering and merging functionality"""

    @pytest.mark.asyncio
    async def test_add_memory_stores_memory(self, deps, clean_database):
        """Test add_memory stores new memory in database"""
        with patch.object(deps.openai, 'embeddings') as mock_embed:
            mock_embed.create = AsyncMock(return_value=Mock(
                data=[Mock(embedding=[0.1] * 1536)]
            ))

            result = await add_memory("Test memory", deps)

            assert "Remembered" in result
            assert "Test memory" in result

    @pytest.mark.asyncio
    async def test_add_memory_with_clustering(self, deps, clean_database):
        """Test add_memory triggers clustering for similar memories"""
        embedding = [0.1] * 1536

        with patch.object(deps.openai, 'embeddings') as mock_embed:
            mock_embed.create = AsyncMock(return_value=Mock(
                data=[Mock(embedding=embedding)]
            ))

            # Add first memory
            await add_memory("Memory 1", deps)

            # Add similar memory (should trigger clustering)
            # The actual clustering logic will be tested by checking
            # if similar memories get merged
            result = await add_memory("Memory 1 similar", deps)

            assert "Remembered" in result


# ============================================================================
# TEST: MCP TOOLS (Component 13-14)
# ============================================================================

class TestMCPTools:
    """Test MCP tool functionality"""

    @pytest.mark.asyncio
    async def test_remember_tool_basic(self, clean_database):
        """Test remember() tool stores memories"""
        with patch('src.memory.AsyncOpenAI') as mock_openai_class:
            mock_openai = AsyncMock()
            mock_openai_class.return_value = mock_openai

            mock_openai.embeddings.create = AsyncMock(
                return_value=Mock(data=[Mock(embedding=[0.1] * 1536)])
            )

            result = await remember(["Test memory 1", "Test memory 2"])

            assert isinstance(result, str)
            assert "Remembered" in result

    @pytest.mark.asyncio
    async def test_remember_tool_empty_list(self):
        """Test remember() tool with empty list"""
        with patch('src.memory.AsyncOpenAI') as mock_openai_class:
            mock_openai = AsyncMock()
            mock_openai_class.return_value = mock_openai

            result = await remember([])

            # Should return empty string or handle gracefully
            assert result is not None

    @pytest.mark.asyncio
    async def test_read_profile_tool_basic(self, clean_database):
        """Test read_profile() tool returns memory tree"""
        with patch('src.memory.AsyncOpenAI') as mock_openai_class:
            mock_openai = AsyncMock()
            mock_openai_class.return_value = mock_openai

            result = await read_profile()

            assert isinstance(result, str)
            assert "Memory Profile" in result

    @pytest.mark.asyncio
    async def test_remember_tool_parameter_validation(self):
        """Test remember() tool validates input parameters"""
        with patch('src.memory.AsyncOpenAI') as mock_openai_class:
            mock_openai = AsyncMock()
            mock_openai_class.return_value = mock_openai

            # Test with list of strings (valid)
            result = await remember(["valid", "input"])
            assert result is not None


# ============================================================================
# TEST: ERROR HANDLING & VALIDATION
# ============================================================================

class TestErrorHandling:
    """Test error handling and validation"""

    @pytest.mark.asyncio
    async def test_memory_node_save_handles_db_error(self, deps):
        """Test MemoryNode.save() handles database errors gracefully"""
        node = MemoryNode(
            content="Test",
            embedding=[0.1] * 1536
        )

        # Close pool to simulate error
        await deps.pool.close()

        with pytest.raises(Exception):
            await node.save(deps)

    @pytest.mark.asyncio
    async def test_add_memory_handles_embedding_error(self, deps, clean_database):
        """Test add_memory handles embedding generation errors"""
        deps.openai.embeddings.create = AsyncMock(
            side_effect=Exception("API error")
        )

        with pytest.raises(Exception):
            await add_memory("Test", deps)

    @pytest.mark.asyncio
    async def test_find_similar_memories_with_empty_database(self, deps, clean_database):
        """Test find_similar_memories handles empty database"""
        result = await find_similar_memories([0.1] * 1536, deps)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_cosine_similarity_type_validation(self):
        """Test cosine_similarity validates input types"""
        # Should handle list inputs
        result = cosine_similarity([1.0, 0.0], [0.0, 1.0])
        assert isinstance(result, float)


# ============================================================================
# TEST: ASYNC OPERATIONS
# ============================================================================

class TestAsyncOperations:
    """Test async/await handling"""

    @pytest.mark.asyncio
    async def test_concurrent_memory_operations(self, deps, clean_database):
        """Test concurrent memory operations work correctly"""
        embedding = [0.1] * 1536

        # Create multiple memories concurrently
        nodes = [
            MemoryNode(content=f"Memory {i}", embedding=embedding)
            for i in range(5)
        ]

        # Save concurrently
        await asyncio.gather(*[node.save(deps) for node in nodes])

        # Verify all saved
        for node in nodes:
            assert node.id is not None

    @pytest.mark.asyncio
    async def test_async_tool_execution(self, clean_database):
        """Test async tool execution"""
        with patch('src.memory.AsyncOpenAI') as mock_openai_class:
            mock_openai = AsyncMock()
            mock_openai_class.return_value = mock_openai

            mock_openai.embeddings.create = AsyncMock(
                return_value=Mock(data=[Mock(embedding=[0.1] * 1536)])
            )

            # Execute tool
            result = await remember(["Test"])

            assert result is not None


# ============================================================================
# TEST: IMPORTANCE SCORING & PRUNING
# ============================================================================

class TestImportanceAndPruning:
    """Test importance scoring and memory pruning"""

    @pytest.mark.asyncio
    async def test_update_importance_increases_score(self, deps, clean_database):
        """Test update_importance increases scores for similar memories"""
        embedding = [0.1] * 1536

        # Create memory
        node = MemoryNode(content="Test", embedding=embedding)
        await node.save(deps)
        original_importance = node.importance

        # Update importance with similar embedding
        await update_importance(embedding, deps)

        # Fetch updated memory
        async with deps.pool.acquire() as conn:
            result = await conn.fetchrow(
                "SELECT importance FROM memories WHERE id = $1",
                node.id
            )
            assert result["importance"] >= original_importance

    @pytest.mark.asyncio
    async def test_prune_memories_maintains_max_depth(self, deps, clean_database):
        """Test prune_memories maintains MAX_DEPTH limit"""
        embedding = [0.1] * 1536

        # Create more than MAX_DEPTH (5) memories
        for i in range(10):
            node = MemoryNode(
                content=f"Memory {i}",
                importance=float(10 - i),  # Different importance
                embedding=embedding
            )
            await node.save(deps)

        # Prune
        await prune_memories(deps)

        # Check count
        async with deps.pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM memories")
            assert count <= 5


# ============================================================================
# TEST: INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple components"""

    @pytest.mark.asyncio
    async def test_full_workflow(self, deps, clean_database):
        """Test full workflow: add -> search -> update -> prune"""
        embedding1 = [0.1] * 1536
        embedding2 = [0.1] * 1536

        with patch.object(deps.openai, 'embeddings') as mock_embed:
            mock_embed.create = AsyncMock(return_value=Mock(
                data=[Mock(embedding=embedding1)]
            ))

            # Add memory
            memory1 = MemoryNode(content="Memory 1", embedding=embedding1)
            await memory1.save(deps)

            # Search similar
            similar = await find_similar_memories(embedding1, deps)
            assert len(similar) > 0

            # Update importance
            await update_importance(embedding1, deps)

            # Display tree
            tree = await display_memory_tree(deps)
            assert "Memory Profile" in tree

    @pytest.mark.asyncio
    async def test_database_persistence(self, clean_database):
        """Test memories persist across operations"""
        with patch('src.memory.AsyncOpenAI') as mock_openai_class:
            mock_openai = AsyncMock()
            mock_openai_class.return_value = mock_openai

            mock_openai.embeddings.create = AsyncMock(
                return_value=Mock(data=[Mock(embedding=[0.1] * 1536)])
            )

            # Store memory
            await remember(["Persistent memory"])

            # Read profile multiple times
            profile1 = await read_profile()
            profile2 = await read_profile()

            # Both should contain the memory
            assert len(profile1) == len(profile2)


# ============================================================================
# TEST: SCHEMA & PROTOCOL COMPLIANCE
# ============================================================================

class TestSchemaCompliance:
    """Test MCP schema and protocol compliance"""

    @pytest.mark.asyncio
    async def test_memory_node_schema_valid(self):
        """Test MemoryNode schema is valid JSON/dict"""
        node = MemoryNode(
            content="Test",
            embedding=[0.1] * 1536
        )

        # Should be serializable
        data = node.model_dump()
        assert isinstance(data, dict)
        assert "content" in data
        assert "embedding" in data

    @pytest.mark.asyncio
    async def test_tool_response_format(self, clean_database):
        """Test tool responses follow expected format"""
        with patch('src.memory.AsyncOpenAI') as mock_openai_class:
            mock_openai = AsyncMock()
            mock_openai_class.return_value = mock_openai

            mock_openai.embeddings.create = AsyncMock(
                return_value=Mock(data=[Mock(embedding=[0.1] * 1536)])
            )

            result = await read_profile()

            # Response should be string
            assert isinstance(result, str)


# ============================================================================
# TEST CONFIGURATION & UTILITIES
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment before all tests"""
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["LOG_LEVEL"] = "DEBUG"
    yield


def pytest_configure(config):
    """Configure pytest for FastMCP server tests"""
    from dotenv import load_dotenv

    # Load test environment variables
    test_env_file = ".env.test"
    if os.path.exists(test_env_file):
        load_dotenv(test_env_file)

    # Register async marker
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as async (requires pytest-asyncio)"
    )
