(function () {
  const config = window.CapitalBotConfig || {
    apiUrl: "/ask",
    title: "Capi",
    subtitle: "Asistente virtual de Canal Capital",
    launcherIcon: "/static/img/chatbot-icon.png",
    primaryColor: "#ef3450",
    secondaryColor: "#0078b8",
    welcomeMessage:
      "Hola, soy Capi! Estoy aquí para ayudarte con información de la intranet, SICC, ERPC, Recursos Humanos, denuncias públicas, salas y soporte TIC."
  };

  const style = document.createElement("style");
  style.innerHTML = `
    :root{
      --cb-red:${config.primaryColor};
      --cb-blue:${config.secondaryColor};
      --cb-dark:#12263f;
      --cb-bg:#f5f7fb;
      --cb-border:#d9e2ec;
      --cb-text:#243447;
      --cb-white:#ffffff;
      --cb-shadow:0 18px 45px rgba(0,0,0,.18);
    }

    #capitalbot-launcher{
    position:fixed;
    right:24px;
    bottom:24px;
    width:92px;
    height:92px;
    border-radius:50%;
    border:4px solid #ef3450;
    padding:0;
    background-color:#ffffff;
    background-image:url("/static/img/chatbot-icon.png?v=5");
    background-size:cover;
    background-position:center center;
    background-repeat:no-repeat;
    box-shadow:0 14px 30px rgba(239,52,80,.35);
    cursor:pointer;
    z-index:999999;
    display:block;
    overflow:hidden;
    transition:transform .2s ease, box-shadow .2s ease;
    }

    #capitalbot-launcher:hover{
      transform:translateY(-2px) scale(1.02);
      box-shadow:0 18px 36px rgba(239,52,80,.42);
    }

    #capitalbot-launcher img{
    display:none !important;
    }

    #capitalbot-panel{
      position:fixed;
      right:24px;
      bottom:110px;
      width:390px;
      height:620px;
      max-height:calc(100vh - 140px);
      background:var(--cb-white);
      border-radius:22px;
      box-shadow:var(--cb-shadow);
      overflow:hidden;
      z-index:999998;
      border:1px solid var(--cb-border);
      display:none;
      flex-direction:column;
      font-family:"Segoe UI", Arial, sans-serif;
    }

    #capitalbot-panel.open{
      display:flex;
      animation:cbFadeIn .2s ease;
    }

    @keyframes cbFadeIn{
      from{opacity:0; transform:translateY(10px) scale(.98);}
      to{opacity:1; transform:translateY(0) scale(1);}
    }

    .cb-header{
      background:linear-gradient(145deg, var(--cb-red), #d92d4b);
      color:var(--cb-white);
      padding:16px 18px;
      display:flex;
      align-items:center;
      justify-content:space-between;
    }

    .cb-header-left{
      display:flex;
      align-items:center;
      gap:12px;
    }

    .cb-avatar{
    width:46px;
    height:46px;
    border-radius:50%;
    border:2px solid rgba(255,255,255,.75);
    background-color:#ffffff;
    background-image:url("/static/img/chatbot-icon.png?v=5");
    background-size:cover;
    background-position:center center;
    background-repeat:no-repeat;
    display:block;
    overflow:hidden;
    flex-shrink:0;
    box-shadow:0 8px 18px rgba(0,0,0,.18);
    }

    .cb-avatar img{
    display:none !important;
    }

    .cb-header h3{
      margin:0;
      font-size:18px;
      line-height:1.1;
    }

    .cb-header p{
      margin:4px 0 0 0;
      font-size:12px;
      opacity:.92;
    }

    .cb-close{
      border:none;
      background:rgba(255,255,255,.12);
      color:#fff;
      width:36px;
      height:36px;
      border-radius:10px;
      cursor:pointer;
      font-size:18px;
    }

    .cb-body{
      flex:1;
      background:linear-gradient(rgba(255,255,255,.95), rgba(255,255,255,.95)), var(--cb-bg);
      padding:16px;
      overflow-y:auto;
    }

    .cb-message{
      display:flex;
      margin-bottom:14px;
    }

    .cb-message.user{
      justify-content:flex-end;
    }

    .cb-bubble{
      max-width:82%;
      padding:12px 14px;
      border-radius:16px;
      line-height:1.5;
      font-size:14px;
      white-space:pre-line;
      word-wrap:break-word;
    }

    .cb-message.bot .cb-bubble{
      background:#eef3f8;
      color:var(--cb-text);
      border-top-left-radius:6px;
      border:1px solid #dde6ee;
    }

    .cb-message.user .cb-bubble{
      background:linear-gradient(145deg, var(--cb-blue), #005f94);
      color:#fff;
      border-top-right-radius:6px;
    }

    .cb-quick{
      padding:0 16px 12px 16px;
      display:flex;
      flex-wrap:wrap;
      gap:8px;
      background:#fff;
    }

    .cb-chip{
      border:1px solid #cfe2f1;
      background:#f3f9fd;
      color:#005f94;
      padding:8px 12px;
      border-radius:999px;
      font-size:12px;
      cursor:pointer;
      transition:.2s ease;
    }

    .cb-chip:hover{
      background:#0078b8;
      color:#fff;
    }

    .cb-input-area{
      padding:14px;
      border-top:1px solid var(--cb-border);
      background:#fff;
      display:flex;
      gap:10px;
    }

    .cb-input{
      flex:1;
      border:1px solid #d4dce5;
      border-radius:14px;
      padding:12px 14px;
      font-size:14px;
      outline:none;
    }

    .cb-input:focus{
      border-color:var(--cb-blue);
      box-shadow:0 0 0 4px rgba(0,120,184,.12);
    }

    .cb-send{
      border:none;
      background:linear-gradient(145deg, var(--cb-red), #d92d4b);
      color:#fff;
      border-radius:14px;
      padding:0 18px;
      font-weight:700;
      cursor:pointer;
    }

    .cb-send:disabled{
      opacity:.65;
      cursor:not-allowed;
    }

    .cb-typing{
      display:inline-flex;
      gap:4px;
      align-items:center;
    }

    .cb-typing span{
      width:6px;
      height:6px;
      background:#76879a;
      border-radius:50%;
      animation:cbBounce 1.2s infinite;
    }

    .cb-typing span:nth-child(2){ animation-delay:.15s; }
    .cb-typing span:nth-child(3){ animation-delay:.3s; }

    @keyframes cbBounce{
      0%,80%,100%{transform:translateY(0); opacity:.45;}
      40%{transform:translateY(-4px); opacity:1;}
    }

    @media (max-width: 520px){
    #capitalbot-panel{
        right:12px;
        left:12px;
        width:auto;
        bottom:98px;
        height:75vh;
    }

    #capitalbot-launcher{
        right:16px;
        bottom:16px;
        width:76px;
        height:76px;
    }
    }
  `;
  document.head.appendChild(style);

  const launcher = document.createElement("button");
  launcher.id = "capitalbot-launcher";
  launcher.setAttribute("aria-label", "Abrir CapitalBot");
  launcher.innerHTML = "";

  const panel = document.createElement("div");
  panel.id = "capitalbot-panel";
  panel.innerHTML = `
    <div class="cb-header">
      <div class="cb-header-left">
        <div class="cb-avatar">
          <img src="${config.launcherIcon}" alt="CapitalBot">
        </div>
        <div>
          <h3>${config.title}</h3>
          <p>${config.subtitle}</p>
        </div>
      </div>
      <button class="cb-close" aria-label="Cerrar">×</button>
    </div>

    <div class="cb-body" id="cbBody">
      <div class="cb-message bot">
        <div class="cb-bubble">${config.welcomeMessage}</div>
      </div>
    </div>

    <div class="cb-quick">
      <button class="cb-chip" data-question="¿Qué es el SICC?">¿Qué es el SICC?</button>
      <button class="cb-chip" data-question="¿Qué es el ERPC?">¿Qué es el ERPC?</button>
      <button class="cb-chip" data-question="¿Cómo solicito una sala?">Solicitar sala</button>
      <button class="cb-chip" data-question="¿Dónde reporto fallas?">Reportar fallas</button>
    </div>

    <form class="cb-input-area" id="cbForm">
      <input id="cbInput" class="cb-input" type="text" placeholder="Escribe tu pregunta..." autocomplete="off" />
      <button id="cbSend" class="cb-send" type="submit">Enviar</button>
    </form>
  `;

  document.body.appendChild(panel);
  document.body.appendChild(launcher);

  const body = panel.querySelector("#cbBody");
  const input = panel.querySelector("#cbInput");
  const form = panel.querySelector("#cbForm");
  const send = panel.querySelector("#cbSend");
  const closeBtn = panel.querySelector(".cb-close");

  function appendMessage(type, text) {
    const wrap = document.createElement("div");
    wrap.className = `cb-message ${type}`;

    const bubble = document.createElement("div");
    bubble.className = "cb-bubble";
    bubble.textContent = text;

    wrap.appendChild(bubble);
    body.appendChild(wrap);
    body.scrollTop = body.scrollHeight;
  }

  function appendTyping() {
    const wrap = document.createElement("div");
    wrap.className = "cb-message bot";
    wrap.id = "cbTyping";

    const bubble = document.createElement("div");
    bubble.className = "cb-bubble";
    bubble.innerHTML = `
      <div class="cb-typing">
        <span></span><span></span><span></span>
      </div>
    `;

    wrap.appendChild(bubble);
    body.appendChild(wrap);
    body.scrollTop = body.scrollHeight;
  }

  function removeTyping() {
    const typing = document.getElementById("cbTyping");
    if (typing) typing.remove();
  }

    function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
    }

    function getHumanDelay() {
    return Math.floor(Math.random() * 1000) + 1000;
    }

    function getConversationId() {
    let conversationId = sessionStorage.getItem("capi_conversation_id");

    if (!conversationId) {
        conversationId = "CAPI-" + Date.now() + "-" + Math.random().toString(36).substring(2, 8).toUpperCase();
        sessionStorage.setItem("capi_conversation_id", conversationId);
    }

    return conversationId;
    }

    async function askBot(question) {
    appendMessage("user", question);
    send.disabled = true;
    appendTyping();

    try {
        const response = await fetch(config.apiUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
        question: question,
        conversation_id: getConversationId()
        })
        });

        if (!response.ok) {
        throw new Error("No fue posible consultar el asistente.");
        }

        const data = await response.json();

        // Delay humano simulado entre 1 y 2 segundos
        await delay(getHumanDelay());

        removeTyping();

        appendMessage(
        "bot",
        data.answer || "No fue posible generar una respuesta en este momento."
        );

    } catch (error) {
        await delay(1000);

        removeTyping();

        appendMessage(
        "bot",
        "Ocurrió un error al consultar el asistente. Intenta nuevamente."
        );

    } finally {
        send.disabled = false;
        input.focus();
    }
    }

  launcher.addEventListener("click", () => {
    panel.classList.toggle("open");
    if (panel.classList.contains("open")) {
      input.focus();
    }
  });

  closeBtn.addEventListener("click", () => {
    panel.classList.remove("open");
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const question = input.value.trim();
    if (!question) return;
    input.value = "";
    await askBot(question);
  });

  panel.querySelectorAll(".cb-chip").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const question = btn.getAttribute("data-question");
      await askBot(question);
    });
  });
})();