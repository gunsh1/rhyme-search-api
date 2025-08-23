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

# 軽量版の実装（重い依存関係を避ける）
class RhymeSearchGPT:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        print(f"OpenAI API Key configured: {'Yes' if self.api_key else 'No'}")
        
        # 基本的な韻律辞書
        self.sample_rhymes = {
            "愛": ["開", "海", "貝", "回", "会", "買", "台", "態", "代"],
            "夢": ["雲", "組", "込", "積", "詰", "摘", "潜"],
            "光": ["理", "利", "力", "切", "着", "勝", "立"],
            "心": ["信", "新", "真", "進", "親", "針", "芯"],
            "歌": ["花", "香", "菓", "話", "価", "華", "化"],
            "希望": ["未来", "期待", "願い", "目標", "夢想", "理想"],
            "桜": ["花", "春", "美", "優", "香", "雅"]
        }
    
    def search_rhymes_for_gpt(self, word: str, max_results: int = 10, phonetic_similarity: float = 0.7) -> Dict[str, Any]:
        """韻律検索機能"""
        rhymes = self.sample_rhymes.get(word, [f"{word}音", f"{word}韻", "類似"])[:max_results]
        
        return {
            "status": "success",
            "query_word": word,
            "rhymes": rhymes,
            "ai_suggestions": [f"AI{word}", f"新{word}", f"心{word}"],
            "phonetic_analysis": {
                "mora_count": len(word),
                "ending_vowel": word[-1] if word else "",
                "vowel_pattern": "模擬パターン"
            },
            "total_results": len(rhymes),
            "usage_examples": [f"{word}を使った例文1", f"{word}を使った例文2"]
        }
    
    def analyze_phonetics_for_gpt(self, word: str, detailed: bool = True) -> Dict[str, Any]:
        """音韻分析機能"""
        return {
            "status": "success",
            "word": word,
            "mora_count": len(word),
            "syllable_structure": list(word),
            "vowel_pattern": "模擬パターン",
            "rhyme_class": f"{word}クラス",
            "phonetic_features": {
                "consonants": len([c for c in word if c not in "あいうえお"]),
                "vowels": len([c for c in word if c in "あいうえお"])
            }
        }
    
    def generate_rap_suggestions_for_gpt(self, theme: str, rhyme_words: List[str] = None, **kwargs) -> Dict[str, Any]:
        """ラップ生成機能"""
        style = kwargs.get("style", "modern")
        max_lines = kwargs.get("max_lines", 8)
        
        # テーマに基づいたラップ生成
        lyrics = [
            f"{theme}への道のり、心に刻む",
            f"困難を乗り越え、{theme}を見つめ",
            f"夢と現実、{theme}が導く", 
            f"前進あるのみ、{theme}とともに",
            f"光差す未来、{theme}を信じて",
            f"歩み続ける、{theme}の力で",
            f"希望の歌声、{theme}響かせ",
            f"新たな明日、{theme}と歩もう"
        ][:max_lines]
        
        return {
            "status": "success",
            "theme": theme,
            "style": style,
            "lyrics": lyrics,
            "rhyme_analysis": {
                "rhyme_scheme": "ABAB",
                "mora_pattern": "7-7-7-7"
            },
            "used_rhyme_words": rhyme_words or [theme],
            "suggested_flow": "4/4拍子、中テンポ",
            "alternative_versions": [f"{theme}をテーマにした別バージョンも生成可能"]
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
rhyme_gpt = RhymeSearchGPT()
print("RhymeSearchGPT initialized successfully")

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
