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

    #capitalbot-panel,
    #capitalbot-panel *,
    #capitalbot-launcher,
    #capitalbot-launcher *{
      box-sizing:border-box !important;
    }

    #capitalbot-panel{
      font-family:"Segoe UI", Arial, sans-serif !important;
      color:#243447 !important;
    }

    #capitalbot-panel button,
    #capitalbot-panel input{
      font-family:"Segoe UI", Arial, sans-serif !important;
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
    background-image:url("${config.launcherIcon}");
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

  #capitalbot-panel .cb-header{
    background:linear-gradient(145deg, var(--cb-red), #d92d4b) !important;
    color:#ffffff !important;
    padding:16px 18px !important;
    display:flex !important;
    align-items:center !important;
    justify-content:space-between !important;
    gap:12px !important;
    box-sizing:border-box !important;
  }

  #capitalbot-panel .cb-header-left{
    display:flex !important;
    align-items:center !important;
    gap:12px !important;
    min-width:0 !important;
  }

    .cb-avatar{
    width:46px;
    height:46px;
    border-radius:50%;
    border:2px solid rgba(255,255,255,.75);
    background-color:#ffffff;
    background-image:url("${config.launcherIcon}");
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

  #capitalbot-panel .cb-header h3{
    margin:0 !important;
    padding:0 !important;
    font-size:18px !important;
    line-height:1.1 !important;
    font-weight:700 !important;
    color:#ffffff !important;
    font-family:"Segoe UI", Arial, sans-serif !important;
  }

  #capitalbot-panel .cb-header p{
    margin:4px 0 0 0 !important;
    padding:0 !important;
    font-size:12px !important;
    line-height:1.2 !important;
    color:#ffffff !important;
    opacity:.95 !important;
    font-family:"Segoe UI", Arial, sans-serif !important;
  }

  #capitalbot-panel .cb-close{
    border:none !important;
    background:rgba(255,255,255,.14) !important;
    color:#ffffff !important;
    width:36px !important;
    height:36px !important;
    min-width:36px !important;
    min-height:36px !important;
    max-width:36px !important;
    max-height:36px !important;
    border-radius:10px !important;
    cursor:pointer !important;
    font-size:22px !important;
    font-weight:700 !important;
    line-height:1 !important;
    padding:0 !important;
    margin:0 !important;
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    text-align:center !important;
    box-shadow:none !important;
    outline:none !important;
    appearance:none !important;
    -webkit-appearance:none !important;
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

    #capitalbot-panel .cb-menu-options{
    display:flex !important;
    flex-wrap:wrap !important;
    gap:8px !important;
    max-width:86% !important;
    background:#eef3f8 !important;
    border:1px solid #dde6ee !important;
    border-radius:16px !important;
    border-top-left-radius:6px !important;
    padding:12px !important;
    box-sizing:border-box !important;
    box-shadow:none !important;
    }

    #capitalbot-panel .cb-menu-options .cb-menu-btn{
      border:1px solid #cfe2f1 !important;
      background:#ffffff !important;
      color:#005f94 !important;
      padding:8px 12px !important;
      border-radius:999px !important;
      font-size:12px !important;
      font-weight:600 !important;
      cursor:pointer !important;
      line-height:1.2 !important;
      min-height:32px !important;
      height:auto !important;
      width:auto !important;
      min-width:auto !important;
      max-width:none !important;
      box-shadow:0 2px 8px rgba(0,120,184,.10) !important;
      text-transform:none !important;
      text-decoration:none !important;
      font-family:"Segoe UI", Arial, sans-serif !important;
      appearance:none !important;
      -webkit-appearance:none !important;
      outline:none !important;
      margin:0 !important;
      display:inline-flex !important;
      align-items:center !important;
      justify-content:center !important;
      white-space:nowrap !important;
    }

    #capitalbot-panel .cb-menu-options .cb-menu-btn:hover{
      background:#0078b8 !important;
      color:#ffffff !important;
      border-color:#0078b8 !important;
      box-shadow:0 4px 12px rgba(0,120,184,.20) !important;
      transform:translateY(-1px) !important;
    }

    #capitalbot-panel .cb-menu-options .cb-menu-btn:focus{
      border-color:#0078b8 !important;
      box-shadow:0 0 0 3px rgba(0,120,184,.14) !important;
    }

    .cb-input-area{
      padding:14px;
      border-top:1px solid var(--cb-border);
      background:#fff;
      display:flex;
      gap:10px;
    }

    #capitalbot-panel .cb-input{
      flex:1 !important;
      border:1px solid #d4dce5 !important;
      border-radius:14px !important;
      padding:12px 14px !important;
      font-size:14px !important;
      line-height:1.2 !important;
      outline:none !important;
      background:#ffffff !important;
      color:#243447 !important;
      height:auto !important;
      min-height:42px !important;
      box-shadow:none !important;
    }

    .cb-input:focus{
      border-color:var(--cb-blue);
      box-shadow:0 0 0 4px rgba(0,120,184,.12);
    }

    #capitalbot-panel .cb-send{
      border:none !important;
      background:linear-gradient(145deg, var(--cb-red), #d92d4b) !important;
      color:#ffffff !important;
      border-radius:14px !important;
      padding:0 18px !important;
      min-width:82px !important;
      height:42px !important;
      font-weight:700 !important;
      font-size:14px !important;
      cursor:pointer !important;
      display:flex !important;
      align-items:center !important;
      justify-content:center !important;
      line-height:1 !important;
      box-shadow:none !important;
      text-transform:none !important;
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

    #capitalbot-panel .cb-menu-options{
    display:flex !important;
    flex-wrap:wrap !important;
    gap:8px !important;
    max-width:86% !important;
    background:#eef3f8 !important;
    border:1px solid #dde6ee !important;
    border-radius:16px !important;
    border-top-left-radius:6px !important;
    padding:12px !important;
    box-sizing:border-box !important;
  }

  #capitalbot-panel .cb-menu-btn{
    border:1px solid #cfe2f1 !important;
    background:#ffffff !important;
    color:#005f94 !important;
    padding:8px 11px !important;
    border-radius:999px !important;
    font-size:12px !important;
    font-weight:600 !important;
    cursor:pointer !important;
    line-height:1 !important;
    min-height:32px !important;
    box-shadow:none !important;
    text-transform:none !important;
    font-family:"Segoe UI", Arial, sans-serif !important;
  }

  #capitalbot-panel .cb-menu-btn:hover{
    background:#0078b8 !important;
    color:#ffffff !important;
  }

    #capitalbot-launcher{
      position:fixed !important;
      right:24px !important;
      bottom:24px !important;
      width:92px !important;
      height:92px !important;
      min-width:92px !important;
      min-height:92px !important;
      max-width:92px !important;
      max-height:92px !important;
      border-radius:50% !important;
      border:4px solid #ef3450 !important;
      padding:0 !important;
      margin:0 !important;
      background-color:#ffffff !important;
      background-image:url("${config.launcherIcon}") !important;
      background-size:cover !important;
      background-position:center center !important;
      background-repeat:no-repeat !important;
      box-shadow:0 14px 30px rgba(239,52,80,.35) !important;
      cursor:pointer !important;
      z-index:999999 !important;
      display:block !important;
      overflow:hidden !important;
      transition:transform .2s ease, box-shadow .2s ease !important;
      appearance:none !important;
      -webkit-appearance:none !important;
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

  function appendMainMenu() {
    const wrap = document.createElement("div");
    wrap.className = "cb-message bot";

    const menu = document.createElement("div");
    menu.className = "cb-menu-options";

    const options = [
      { label: "Intranet", question: "¿Qué puedo hacer en la intranet?" },
      { label: "SICC", question: "¿Qué es el SICC?" },
      { label: "ERPC", question: "¿Qué es el ERPC?" },
      { label: "Salas", question: "¿Cómo solicito una sala?" },
      { label: "Denuncias", question: "¿Cómo registro una denuncia pública?" },
      { label: "RR. HH.", question: "¿Qué contiene Recursos Humanos?" },
      { label: "Soporte TIC", question: "¿Dónde reporto fallas?" }
    ];

    options.forEach((option) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "cb-menu-btn";
      btn.textContent = option.label;

      btn.addEventListener("click", async () => {
        await askBot(option.question);
      });

      menu.appendChild(btn);
    });

    wrap.appendChild(menu);
    body.appendChild(wrap);
    body.scrollTop = body.scrollHeight;
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

        if (data.source_type === "no_match") {
          appendMessage(
            "bot",
            data.answer || "Lo siento, no logro entender tu consulta con la información disponible. Puedo ayudarte con los siguientes temas:"
          );

          appendMainMenu();
        } else {
          appendMessage(
            "bot",
            data.answer || "No fue posible generar una respuesta en este momento."
          );
        }

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

})();