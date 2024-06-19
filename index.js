async function submitCode() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const code = document.getElementById("code").value;

  // 데이터 유효성 검사
  if (!username || !password || !code) {
    alert("입력란을 작성해주세요.");
    return;
  }

  // API 요청을 위한 데이터
  const data = {
    username: username,
    password: password,
    code: code,
  };

  // 관리 서버 URL 설정 (실제 URL로 변경 필요)
  const apiUrl = "http://<manage-server-url>/submission";

  try {
    const response = await axios.post(apiUrl, data, {
      headers: {
        "Content-Type": "application/json",
      },
    });

    // 응답 처리
    if (response.status === 200) {
      alert(`Code submitted successfully! Submission ID: ${response.data.id}`);
    } else {
      alert(`Error: ${response.data.message}`);
    }
  } catch (error) {
    if (error.response) {
      // 서버가 응답했지만, 응답 상태 코드가 2xx가 아닌 경우
      alert(`ERROR: ${error.response.data.message}`);
    } else if (error.request) {
      // 요청이 전송되었지만, 응답이 없었던 경우
      console.error("ERROR:", error.request);
      alert("서버로부터 응답이 없습니다.");
    } else {
      // 요청을 설정 중에 발생한 오류
      console.error("ERROR:", error.message);
      alert("요청을 처리하는 도중에 오류가 발생했습니다.");
    }
  }
}

document.getElementById("submit-btn").addEventListener("click", (event) => {
  event.preventDefault();
  submitCode();
});
