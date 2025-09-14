
CURSOR MCP SETTING GUIDE

컨텍스트
Model Context Protocol (MCP)
MCP로 외부 도구와 데이터 소스를 Cursor에 연결하기

​
MCP란?
Model Context Protocol(MCP)은 Cursor가 외부 도구와 데이터 소스에 연결하도록 해줘.
​
왜 MCP를 써?
MCP는 Cursor를 외부 시스템과 데이터에 연결해. 프로젝트 구조를 매번 설명하는 대신, 쓰는 도구와 바로 통합하면 돼.
stdout에 출력하거나 HTTP 엔드포인트를 제공할 수 있는 언어라면 뭐든 MCP 서버를 만들 수 있어 — Python, JavaScript, Go 등.
​
동작 방식
MCP 서버는 프로토콜을 통해 기능을 노출해서 Cursor를 외부 도구나 데이터 소스와 연결해.
Cursor는 세 가지 전송 방식을 지원해:
Transport	Execution environment	Deployment	Users	Input	Auth
stdio	Local	Cursor manages	Single user	Shell command	Manual
SSE	Local/Remote	Deploy as server	Multiple users	URL to an SSE endpoint	OAuth
Streamable HTTP	Local/Remote	Deploy as server	Multiple users	URL to an HTTP endpoint	OAuth
​
프로토콜 지원
Cursor는 다음 MCP 프로토콜 기능을 지원해:
Feature	Support	Description
Tools	Supported	AI 모델이 실행할 함수
Prompts	Supported	사용자용 템플릿 메시지와 워크플로
Roots	Supported	서버가 작업 범위로 삼을 URI 또는 파일 시스템 경계를 질의
Elicitation	Supported	서버가 사용자에게 추가 정보를 요청
​
MCP 서버 설치
​
원클릭 설치
컬렉션에서 MCP 서버를 설치하고 OAuth로 인증해.
Browse MCP Tools
사용 가능한 MCP 서버 둘러보기
Add to Cursor Button
“Add to Cursor” 버튼 만들기
​
mcp.json 사용
JSON 파일로 커스텀 MCP 서버를 구성해:

CLI Server - Node.js

CLI Server - Python

Remote Server

Copy

Ask AI
{
  "mcpServers": {
    "server-name": {
      "command": "python",
      "args": ["mcp-server.py"],
      "env": {
        "API_KEY": "value"
      }
    }
  }
}
​
Extension API 사용
프로그램적으로 MCP 서버를 등록하려면 Cursor는 mcp.json 파일을 수정하지 않고도 동적으로 구성할 수 있는 Extension API를 제공해. 엔터프라이즈 환경이나 자동화된 셋업 워크플로에 특히 유용해.
MCP Extension API Reference
vscode.cursor.mcp.registerServer()로 프로그램matically MCP 서버를 등록하는 방법 알아보기
​
구성 위치
Project Configuration
프로젝트 전용 도구를 위해 프로젝트에 .cursor/mcp.json을 만들어.
Global Configuration
어디서나 사용할 도구를 위해 홈 디렉터리에 ~/.cursor/mcp.json을 만들어.
​
인증
MCP 서버는 인증에 환경 변수를 사용해. API 키와 토큰은 설정을 통해 전달해.
Cursor는 필요한 서버에 대해 OAuth를 지원해.
​
채팅에서 MCP 사용하기
Composer Agent는 관련 있을 때 Available Tools 아래의 MCP 도구를 자동으로 써. 특정 도구 이름을 직접 말하거나 필요한 걸 설명해 줘. 설정에서 도구를 켜거나 끌 수도 있어.
​
도구 토글
채팅 인터페이스에서 MCP 도구를 바로 켜거나 꺼. 도구 목록에서 도구 이름을 클릭해 토글해. 비활성화된 도구는 컨텍스트에 로드되지도 않고 Agent가 쓸 수도 없어.
​
도구 승인
기본적으로 Agent는 MCP 도구를 사용하기 전에 승인을 요청해. 인자를 보려면 도구 이름 옆 화살표를 클릭해.

​
자동 실행
질문 없이 Agent가 MCP 도구를 쓰도록 자동 실행을 켜. 터미널 명령처럼 동작해. Yolo 모드에 대해 더 알아보기는 여기를 참고해.
​
도구 응답
Cursor는 채팅에서 인자와 응답을 펼쳐볼 수 있는 뷰로 결과를 보여줘:

​
컨텍스트로서의 이미지
MCP 서버는 스크린샷, 다이어그램 등 이미지를 반환할 수 있어. base64로 인코딩된 문자열로 반환해:

Copy

Ask AI
const RED_CIRCLE_BASE64 = "/9j/4AAQSkZJRgABAgEASABIAAD/2w...";
// ^ 가독성을 위해 전체 base64는 생략

server.tool("generate_image", async (params) => {
  return {
    content: [
      {
        type: "image",
        data: RED_CIRCLE_BASE64,
        mimeType: "image/jpeg",
      },
    ],
  };
});
구현 세부 정보는 이 example server를 참고해. Cursor는 반환된 이미지를 채팅에 첨부해. 모델이 이미지를 지원하면 분석해.
​
보안 고려 사항
MCP 서버를 설치할 때는 다음 보안 모범 사례를 꼭 챙겨줘:
소스 검증: 신뢰할 수 있는 개발자와 리포지토리에서 제공하는 MCP 서버만 설치하기
권한 검토: 서버가 어떤 데이터와 API에 접근하는지 확인하기
API 키 제한: 필요한 최소 권한만 가진 제한된 API 키 사용하기
코드 감사: 중요한 통합의 경우, 서버의 소스 코드를 직접 검토하기
MCP 서버는 외부 서비스에 접근하고 너를 대신해 코드를 실행할 수 있어. 설치 전에 서버가 무엇을 하는지 항상 충분히 이해해둬.
​
실전 예시
MCP가 실제로 어떻게 쓰이는지 보려면 웹 개발 가이드를 확인해봐. 이 가이드는 개발 워크플로에 Linear, Figma, 그리고 브라우저 도구를 통합하는 방법을 보여줘.