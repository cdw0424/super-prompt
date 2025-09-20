# packages/core-py/super_prompt/core/memory_manager.py
"""
메모리 및 스팬 관리 기능
"""

import os
import sys
import sqlite3
import time
import json
import traceback
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import contextmanager


class SpanManager:
    def __init__(self):
        self.spans: Dict[str, Dict[str, Any]] = {}
        self._span_counter = 0
        self._init_db()

    def _init_db(self):
        """메모리 데이터베이스 초기화"""
        # 데이터베이스 경로 설정
        db_path = Path.home() / ".super-prompt" / "memory" / "spans.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS spans (
                id TEXT PRIMARY KEY,
                command_id TEXT,
                user_id TEXT,
                start_time REAL,
                end_time REAL,
                duration REAL,
                status TEXT,
                meta TEXT,
                events TEXT,
                extra TEXT
            )
        """
        )
        self.conn.commit()

    def start_span(self, meta: Dict[str, Any]) -> str:
        """새로운 span 시작"""
        span_id = f"span_{self._span_counter}"
        self._span_counter += 1

        self.spans[span_id] = {
            "id": span_id,
            "start_time": time.time(),
            "meta": meta,
            "events": [],
            "status": "active",
        }

        print(
            f"-------- memory: span started {span_id} for {meta.get('commandId', 'unknown')}",
            file=sys.stderr,
            flush=True,
        )
        return span_id

    def write_event(self, span_id: str, event: Dict[str, Any]) -> None:
        """span에 이벤트 기록"""
        if span_id in self.spans:
            event_with_time = {"timestamp": time.time(), **event}
            self.spans[span_id]["events"].append(event_with_time)
            print(f"-------- memory: event recorded in {span_id}", file=sys.stderr, flush=True)

    def end_span(
        self, span_id: str, status: str = "ok", extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """span 종료"""
        if span_id in self.spans:
            span = self.spans[span_id]
            span["end_time"] = time.time()
            span["duration"] = span["end_time"] - span["start_time"]
            span["status"] = status
            if extra:
                span["extra"] = extra

            print(
                f"-------- memory: span ended {span_id} status={status} duration={span['duration']:.2f}s",
                file=sys.stderr,
                flush=True,
            )

            # 데이터베이스에 저장
            self._save_span_to_db(span)

    def _save_span_to_db(self, span: Dict[str, Any]) -> None:
        """span을 데이터베이스에 저장"""
        try:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO spans
                (id, command_id, user_id, start_time, end_time, duration, status, meta, events, extra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    span["id"],
                    span["meta"].get("commandId", ""),
                    span["meta"].get("userId", ""),
                    span["start_time"],
                    span.get("end_time", 0),
                    span.get("duration", 0),
                    span.get("status", "unknown"),
                    json.dumps(span["meta"]),
                    json.dumps(span["events"]),
                    json.dumps(span.get("extra", {})),
                ),
            )
            self.conn.commit()
            print(
                f"-------- memory: span {span['id']} saved to database", file=sys.stderr, flush=True
            )
        except Exception as e:
            print(
                f"-------- memory: failed to save span {span['id']}: {e}",
                file=sys.stderr,
                flush=True,
            )


class ProgressIndicator:
    """실시간 진행상황 표시를 위한 유틸리티 클래스"""

    def __init__(self):
        self.animation_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.frame_index = 0

    def show_progress(self, message: str, step: int = 0, total: int = 0) -> None:
        """진행상황을 표시"""
        frame = self.animation_frames[self.frame_index % len(self.animation_frames)]
        self.frame_index += 1

        if total > 0 and step > 0:
            progress = f"[{step}/{total}] "
        else:
            progress = ""

        print(f"-------- {frame} {progress}{message}", file=sys.stderr, flush=True)

    def show_success(self, message: str) -> None:
        """성공 메시지를 표시"""
        print(f"-------- ✅ {message}", file=sys.stderr, flush=True)

    def show_error(self, message: str) -> None:
        """오류 메시지를 표시"""
        print(f"-------- ❌ {message}", file=sys.stderr, flush=True)

    def show_info(self, message: str) -> None:
        """정보 메시지를 표시"""
        print(f"-------- ℹ️  {message}", file=sys.stderr, flush=True)

    def show_warning(self, message: str) -> None:
        """경고 메시지를 표시"""
        print(f"-------- ⚠️  {message}", file=sys.stderr, flush=True)


# 전역 span 관리자
span_manager = SpanManager()

# 전역 진행상황 표시기
progress = ProgressIndicator()

# Context Cache 통합
from ..context.cache import ContextCache

# 전역 context cache
context_cache = ContextCache()


# 통합 메모리 및 캐시 관리 함수들
def get_memory_stats() -> Dict[str, Any]:
    """통합 메모리 통계 반환"""
    try:
        span_stats = {
            "active_spans": len(span_manager.spans),
            "total_spans": span_manager._span_counter,
        }

        cache_stats = context_cache.get_stats()

        return {
            "span_manager": span_stats,
            "context_cache": cache_stats,
            "timestamp": time.time()
        }
    except Exception as e:
        return {"error": str(e), "timestamp": time.time()}

def clear_all_caches() -> Dict[str, Any]:
    """모든 캐시 시스템 초기화"""
    try:
        # Context cache 초기화
        context_cache.clear()

        # Span manager 초기화 (선택적)
        # span_manager.spans.clear()  # 활성 span들 유지
        # span_manager._span_counter = 0  # 카운터 리셋

        return {
            "status": "success",
            "message": "All caches cleared successfully",
            "context_cache_cleared": True,
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Cache clear failed: {str(e)}",
            "timestamp": time.time()
        }

def cleanup_expired_data(max_age_hours: int = 24) -> Dict[str, Any]:
    """만료된 데이터 정리"""
    try:
        max_age_seconds = max_age_hours * 3600

        # Context cache 정리
        expired_context = context_cache.cleanup_expired(max_age_seconds)

        # Span 데이터 정리 (선택적 - DB에서 직접 처리)
        # span_manager._cleanup_old_spans(max_age_seconds)

        return {
            "status": "success",
            "expired_context_entries": expired_context,
            "max_age_hours": max_age_hours,
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Cleanup failed: {str(e)}",
            "timestamp": time.time()
        }

# Span 컨텍스트 매니저
@contextmanager
def memory_span(command_id: str, user_id: Optional[str] = None):
    """메모리 span 컨텍스트 매니저"""
    span_id = span_manager.start_span({"commandId": command_id, "userId": user_id})

    try:
        yield span_id
    except Exception as e:
        stack = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        span_manager.write_event(
            span_id,
            {"type": "error", "message": str(e), "stack": stack},
        )
        span_manager.end_span(span_id, "error", {"error": str(e), "stack": stack})
        raise
    else:
        span_manager.end_span(span_id, "ok")


# Export memory_span for external use
