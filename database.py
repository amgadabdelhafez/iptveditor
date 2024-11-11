from datetime import datetime
from typing import Optional, Dict, Any
import json
import logging
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Create database engine
engine = create_engine('sqlite:///cache.db')
Base = declarative_base()

class CacheStats:
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.logger = logging.getLogger(__name__)
    
    def record_hit(self, cache_type: str):
        self.hits += 1
        self.logger.info(f"Cache HIT for {cache_type} (Hit rate: {self.hit_rate:.1%})")
    
    def record_miss(self, cache_type: str):
        self.misses += 1
        self.logger.info(f"Cache MISS for {cache_type} (Hit rate: {self.hit_rate:.1%})")
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def report(self):
        total = self.hits + self.misses
        if total > 0:
            self.logger.info(
                f"Cache Statistics - Hits: {self.hits}, Misses: {self.misses}, "
                f"Hit Rate: {self.hit_rate:.1%}"
            )

class TMDBSearchCache(Base):
    __tablename__ = 'tmdb_search_cache'
    
    id = Column(Integer, primary_key=True)
    query = Column(String(255), nullable=False)
    response = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Index for faster lookups
    __table_args__ = (Index('idx_query', 'query'),)
    
    @property
    def response_json(self) -> Dict[str, Any]:
        """Get response as JSON object"""
        return json.loads(self.response)

class TMDBDetailsCache(Base):
    __tablename__ = 'tmdb_details_cache'
    
    id = Column(Integer, primary_key=True)
    tmdb_id = Column(Integer, nullable=False, unique=True)
    response = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def response_json(self) -> Dict[str, Any]:
        """Get response as JSON object"""
        return json.loads(self.response)

class IPTVEditorEpisodesCache(Base):
    __tablename__ = 'iptveditor_episodes_cache'
    
    id = Column(Integer, primary_key=True)
    show_id = Column(Integer, nullable=False, unique=True)  # Changed from series_id to show_id
    response = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def response_json(self) -> Dict[str, Any]:
        """Get response as JSON object"""
        return json.loads(self.response)

class IPTVEditorUpdateCache(Base):
    __tablename__ = 'iptveditor_update_cache'
    
    id = Column(Integer, primary_key=True)
    show_id = Column(Integer, nullable=False)
    tmdb_id = Column(Integer, nullable=False)
    category_id = Column(Integer, nullable=False)
    response = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite index for faster lookups
    __table_args__ = (
        Index('idx_show_tmdb_category', 'show_id', 'tmdb_id', 'category_id'),
    )
    
    @property
    def response_json(self) -> Dict[str, Any]:
        """Get response as JSON object"""
        return json.loads(self.response)

class CacheManager:
    def __init__(self):
        Base.metadata.create_all(engine)
        Session_factory = sessionmaker(bind=engine)
        self.Session = Session_factory
        self.stats = CacheStats()
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.Session()
    
    def cache_tmdb_search(self, query: str, response: Dict[str, Any]) -> None:
        """Cache TMDB search response"""
        with self.get_session() as session:
            cache_entry = session.query(TMDBSearchCache).filter_by(query=query).first()
            if cache_entry:
                cache_entry.response = json.dumps(response)
                cache_entry.updated_at = datetime.utcnow()
            else:
                cache_entry = TMDBSearchCache(
                    query=query,
                    response=json.dumps(response)
                )
                session.add(cache_entry)
            session.commit()
    
    def get_tmdb_search(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached TMDB search response"""
        with self.get_session() as session:
            cache_entry = session.query(TMDBSearchCache).filter_by(query=query).first()
            if cache_entry:
                self.stats.record_hit("TMDB Search")
                return cache_entry.response_json
            self.stats.record_miss("TMDB Search")
            return None
    
    def cache_tmdb_details(self, tmdb_id: int, response: Dict[str, Any]) -> None:
        """Cache TMDB details response"""
        with self.get_session() as session:
            cache_entry = session.query(TMDBDetailsCache).filter_by(tmdb_id=tmdb_id).first()
            if cache_entry:
                cache_entry.response = json.dumps(response)
                cache_entry.updated_at = datetime.utcnow()
            else:
                cache_entry = TMDBDetailsCache(
                    tmdb_id=tmdb_id,
                    response=json.dumps(response)
                )
                session.add(cache_entry)
            session.commit()
    
    def get_tmdb_details(self, tmdb_id: int) -> Optional[Dict[str, Any]]:
        """Get cached TMDB details response"""
        with self.get_session() as session:
            cache_entry = session.query(TMDBDetailsCache).filter_by(tmdb_id=tmdb_id).first()
            if cache_entry:
                self.stats.record_hit("TMDB Details")
                return cache_entry.response_json
            self.stats.record_miss("TMDB Details")
            return None
    
    def cache_iptveditor_episodes(self, show_id: int, response: Dict[str, Any]) -> None:
        """Cache IPTV Editor episodes response"""
        with self.get_session() as session:
            cache_entry = session.query(IPTVEditorEpisodesCache).filter_by(show_id=show_id).first()
            if cache_entry:
                cache_entry.response = json.dumps(response)
                cache_entry.updated_at = datetime.utcnow()
            else:
                cache_entry = IPTVEditorEpisodesCache(
                    show_id=show_id,
                    response=json.dumps(response)
                )
                session.add(cache_entry)
            session.commit()
    
    def get_iptveditor_episodes(self, show_id: int) -> Optional[Dict[str, Any]]:
        """Get cached IPTV Editor episodes response"""
        with self.get_session() as session:
            cache_entry = session.query(IPTVEditorEpisodesCache).filter_by(show_id=show_id).first()
            if cache_entry:
                self.stats.record_hit("IPTV Editor Episodes")
                return cache_entry.response_json
            self.stats.record_miss("IPTV Editor Episodes")
            return None
    
    def cache_iptveditor_update(
        self, show_id: int, tmdb_id: int, category_id: int, response: Dict[str, Any]
    ) -> None:
        """Cache IPTV Editor update response"""
        with self.get_session() as session:
            cache_entry = session.query(IPTVEditorUpdateCache).filter_by(
                show_id=show_id,
                tmdb_id=tmdb_id,
                category_id=category_id
            ).first()
            if cache_entry:
                cache_entry.response = json.dumps(response)
                cache_entry.updated_at = datetime.utcnow()
            else:
                cache_entry = IPTVEditorUpdateCache(
                    show_id=show_id,
                    tmdb_id=tmdb_id,
                    category_id=category_id,
                    response=json.dumps(response)
                )
                session.add(cache_entry)
            session.commit()
    
    def get_iptveditor_update(
        self, show_id: int, tmdb_id: int, category_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get cached IPTV Editor update response"""
        with self.get_session() as session:
            cache_entry = session.query(IPTVEditorUpdateCache).filter_by(
                show_id=show_id,
                tmdb_id=tmdb_id,
                category_id=category_id
            ).first()
            if cache_entry:
                self.stats.record_hit("IPTV Editor Update")
                return cache_entry.response_json
            self.stats.record_miss("IPTV Editor Update")
            return None
    
    def report_stats(self):
        """Report cache statistics"""
        self.stats.report()

# Create global cache manager instance
cache_manager = CacheManager()
