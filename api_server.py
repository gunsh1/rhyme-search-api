from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import os
from typing import List, Dict, Any, Optional

# 相対インポート用の設定
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.rhyme_search.openai_integration import RhymeSearchGPT
except ImportError:
    print("Warning: Could not import RhymeSearchGPT. Creating mock implementation.")
    
    class RhymeSearchGPT:
        def __init__(self):
            pass
        
        def search_rhymes_for_gpt(self, word: str, **kwargs) -> Dict[str, Any]:
            return {
                "status": "mock",
                "query_word": word,
                "rhymes": ["サンプル", "テスト", "模擬"],
                "message": "これはモック実装です。本機能を使用するには環境をセットアップしてください。"
            }
        
        def analyze_phonetics_for_gpt(self, word: str, **kwargs) -> Dict[str, Any]:
            return {
                "status": "mock",
                "word": word,
                "phonetic_analysis": "モック音韻分析",
                "message": "これはモック実装です。本機能を使用するには環境をセットアップしてください。"
            }
        
        def generate_rap_suggestions_for_gpt(self, theme: str, rhyme_words: List[str] = None, **kwargs) -> Dict[str, Any]:
            # より具体的なモックデータを提供
            mock_lyrics = [
                f"{theme}への道のり、心に刻む",
                f"困難を乗り越え、{theme}を見つめ",
                f"夢と現実、{theme}が導く",
                f"前進あるのみ、{theme}とともに"
            ]
            return {
                "status": "mock",
                "theme": theme,
                "style": kwargs.get("style", "modern"),
                "lyrics": mock_lyrics,
                "rhyme_analysis": {
                    "rhyme_scheme": "ABAB",
                    "mora_pattern": "7-7-7-7"
                },
                "used_rhyme_words": rhyme_words or [theme],
                "suggested_flow": "4/4拍子、中テンポ",
                "alternative_versions": [f"{theme}をテーマにした別バージョンも生成可能"],
                "message": "OpenAI API Key設定後、より高品質なラップが生成されます。"
            }

app = FastAPI(
    title="Rhyme Search API for ChatGPT Custom GPT",
    description="ChatGPT Custom GPT用の韻律検索APIシステム",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# CORS設定（ChatGPT Custom GPTからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com", "*"],  # 本番環境では適切に制限
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# RhymeSearchGPTインスタンスを初期化
try:
    rhyme_gpt = RhymeSearchGPT()
    print("RhymeSearchGPT initialized successfully")
except Exception as e:
    print(f"Failed to initialize RhymeSearchGPT: {e}")
    rhyme_gpt = RhymeSearchGPT()  # モック実装にフォールバック

# リクエストモデル定義
class RhymeSearchRequest(BaseModel):
    word: str
    max_results: Optional[int] = 10
    phonetic_similarity: Optional[float] = 0.7

class PhoneticAnalysisRequest(BaseModel):
    word: str
    detailed: Optional[bool] = True

class RapSuggestionRequest(BaseModel):
    theme: str
    rhyme_words: Optional[List[str]] = None
    style: Optional[str] = "modern"
    max_lines: Optional[int] = 8

@app.get("/")
async def root():
    """ヘルスチェックエンドポイント"""
    return {
        "message": "Rhyme Search API for ChatGPT Custom GPT",
        "status": "active",
        "version": "1.0.0",
        "endpoints": {
            "search_rhymes": "/api/search-rhymes",
            "analyze_phonetics": "/api/analyze-phonetics", 
            "generate_rap": "/api/generate-rap-suggestions",
            "openapi_schema": "/openapi.json"
        }
    }

@app.post("/api/search-rhymes")
async def search_rhymes(request: RhymeSearchRequest):
    """
    指定した単語と韻を踏む単語を検索
    ChatGPT Custom GPT から使用されるメインエンドポイント
    """
    try:
        result = rhyme_gpt.search_rhymes_for_gpt(
            word=request.word,
            max_results=request.max_results,
            phonetic_similarity=request.phonetic_similarity
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"韻律検索エラー: {str(e)}")

@app.post("/api/analyze-phonetics")
async def analyze_phonetics(request: PhoneticAnalysisRequest):
    """
    単語の音韻構造を詳細に分析
    """
    try:
        result = rhyme_gpt.analyze_phonetics_for_gpt(
            word=request.word,
            detailed=request.detailed
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"音韻分析エラー: {str(e)}")

@app.post("/api/generate-rap-suggestions")
async def generate_rap_suggestions(request: RapSuggestionRequest):
    """
    テーマに基づいてラップ歌詞を提案
    """
    try:
        # より堅牢なエラーハンドリング
        result = rhyme_gpt.generate_rap_suggestions_for_gpt(
            theme=request.theme,
            rhyme_words=request.rhyme_words,
            style=request.style,
            max_lines=request.max_lines
        )
        
        # 成功レスポンスを保証
        if not result:
            result = {
                "status": "fallback",
                "theme": request.theme,
                "lyrics": [f"{request.theme}への思い、心に響く"],
                "message": "基本的なラップを生成しました"
            }
        
        return JSONResponse(content=result, status_code=200)
        
    except Exception as e:
        # エラー時のフォールバック応答
        fallback_result = {
            "status": "error_fallback",
            "theme": request.theme,
            "style": request.style or "modern",
            "lyrics": [
                f"{request.theme}の光、闇を照らす",
                f"困難越えて、{request.theme}へ向かう",
                f"信じる心、{request.theme}とともに",
                f"未来へ歩む、{request.theme}の道"
            ],
            "rhyme_analysis": {"pattern": "ABAB"},
            "message": f"サーバーエラーのため基本ラップを生成: {str(e)}"
        }
        return JSONResponse(content=fallback_result, status_code=200)

@app.get("/health")
async def health_check():
    """ヘルスチェック（デプロイメント用）"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@app.get("/api/health")
async def api_health_check():
    """API ヘルスチェック（Railway用）"""
    return {
        "status": "healthy", 
        "service": "Rhyme Search API",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Rhyme Search API server on port {port}")
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0", 
        port=port,
        reload=False,
        access_log=True
    )
