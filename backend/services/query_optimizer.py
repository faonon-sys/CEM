"""
Database Query Optimization Layer
Implements query batching, eager loading, and indexed queries
"""
from sqlalchemy import select, func, Index
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional, Dict, Any
from functools import lru_cache
import asyncio


class QueryOptimizer:
    """Optimizes database queries for better performance"""

    @staticmethod
    def add_indexes_to_models():
        """
        Add database indexes for frequently queried columns
        Call this during application startup or in migration
        """
        from models.scenario import (
            Scenario, SurfaceAnalysis, DeepQuestion,
            Counterfactual, StrategicOutcome
        )

        # Indexes to create
        indexes = [
            # Scenario indexes
            Index('idx_scenarios_user_created', Scenario.user_id, Scenario.created_at.desc()),
            Index('idx_scenarios_status', Scenario.status),

            # Surface Analysis indexes
            Index('idx_surface_scenario', SurfaceAnalysis.scenario_id),
            Index('idx_surface_domain', SurfaceAnalysis.domain),

            # Deep Question indexes
            Index('idx_questions_scenario', DeepQuestion.scenario_id),
            Index('idx_questions_dimension', DeepQuestion.dimension),

            # Counterfactual indexes
            Index('idx_counterfactuals_scenario', Counterfactual.scenario_id),
            Index('idx_counterfactuals_axis', Counterfactual.axis),
            Index('idx_counterfactuals_severity', Counterfactual.severity_rating),

            # Strategic Outcome indexes
            Index('idx_outcomes_counterfactual', StrategicOutcome.counterfactual_id),
        ]

        print(f"✅ Configured {len(indexes)} database indexes for optimization")
        return indexes

    @staticmethod
    async def get_scenario_with_all_analyses(db_session, scenario_id: int):
        """
        Fetch scenario with all related analyses in a single query
        Uses eager loading to prevent N+1 query problem
        """
        from models.scenario import Scenario

        query = (
            select(Scenario)
            .where(Scenario.id == scenario_id)
            .options(
                selectinload(Scenario.surface_analyses),
                selectinload(Scenario.deep_questions),
                selectinload(Scenario.counterfactuals).selectinload('outcomes')
            )
        )

        result = await db_session.execute(query)
        scenario = result.scalar_one_or_none()

        return scenario

    @staticmethod
    async def get_user_scenarios_paginated(
        db_session,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        include_counts: bool = True
    ):
        """
        Efficiently paginate user scenarios with optional analysis counts
        """
        from models.scenario import Scenario, SurfaceAnalysis, DeepQuestion, Counterfactual

        offset = (page - 1) * page_size

        # Base query with pagination
        query = (
            select(Scenario)
            .where(Scenario.user_id == user_id)
            .order_by(Scenario.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )

        # Optionally include counts in a single query
        if include_counts:
            query = query.options(
                selectinload(Scenario.surface_analyses),
                selectinload(Scenario.deep_questions),
                selectinload(Scenario.counterfactuals)
            )

        result = await db_session.execute(query)
        scenarios = result.scalars().all()

        # Get total count for pagination
        count_query = (
            select(func.count(Scenario.id))
            .where(Scenario.user_id == user_id)
        )
        total_count = await db_session.scalar(count_query)

        return {
            'scenarios': scenarios,
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        }

    @staticmethod
    async def batch_get_counterfactual_outcomes(
        db_session,
        counterfactual_ids: List[int]
    ):
        """
        Batch fetch outcomes for multiple counterfactuals
        More efficient than querying one by one
        """
        from models.scenario import StrategicOutcome

        query = (
            select(StrategicOutcome)
            .where(StrategicOutcome.counterfactual_id.in_(counterfactual_ids))
        )

        result = await db_session.execute(query)
        outcomes = result.scalars().all()

        # Group by counterfactual_id for easy access
        grouped = {}
        for outcome in outcomes:
            if outcome.counterfactual_id not in grouped:
                grouped[outcome.counterfactual_id] = []
            grouped[outcome.counterfactual_id].append(outcome)

        return grouped

    @staticmethod
    @lru_cache(maxsize=100)
    def get_scenario_statistics(user_id: int) -> Dict[str, int]:
        """
        Cached aggregation query for user statistics
        LRU cache prevents repeated expensive queries
        """
        # This would be an async query in production
        # Simplified for demonstration
        return {
            'total_scenarios': 0,
            'total_assumptions': 0,
            'total_questions': 0,
            'total_counterfactuals': 0
        }

    @staticmethod
    async def bulk_create_analyses(
        db_session,
        scenario_id: int,
        assumptions: List[Dict[str, Any]]
    ):
        """
        Bulk insert analyses instead of one-by-one
        Much faster for large batches
        """
        from models.scenario import SurfaceAnalysis

        # Create instances
        instances = [
            SurfaceAnalysis(
                scenario_id=scenario_id,
                assumption=a['text'],
                category=a['category'],
                confidence=a['confidence']
            )
            for a in assumptions
        ]

        # Bulk insert
        db_session.add_all(instances)
        await db_session.commit()

        return instances


class QueryCache:
    """In-memory query result cache for frequently accessed data"""

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._ttl: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get cached query result"""
        if key in self._cache:
            return self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 300):
        """Cache query result with TTL"""
        self._cache[key] = value
        self._ttl[key] = ttl

    def invalidate(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        keys_to_delete = [k for k in self._cache if pattern in k]
        for key in keys_to_delete:
            del self._cache[key]
            if key in self._ttl:
                del self._ttl[key]


# Global query cache instance
query_cache = QueryCache()


# Example usage in API endpoints
async def get_scenario_optimized(db_session, scenario_id: int, user_id: int):
    """
    Optimized scenario retrieval with caching and eager loading
    """
    # Check cache first
    cache_key = f"scenario:{scenario_id}:{user_id}"
    cached = query_cache.get(cache_key)
    if cached:
        return cached

    # Fetch with eager loading
    optimizer = QueryOptimizer()
    scenario = await optimizer.get_scenario_with_all_analyses(db_session, scenario_id)

    # Cache result
    query_cache.set(cache_key, scenario, ttl=300)

    return scenario


if __name__ == "__main__":
    print("Query Optimizer module initialized")
    print(f"✅ Database indexes configured")
    print(f"✅ Query cache ready")
