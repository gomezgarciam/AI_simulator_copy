UI_TEXTS = {
    "English": {
        # Setup
        "setup_title": "Roleplay Setup",
        "setup_subtitle": "Configure the buyer persona, account context, and enrichment inputs before launching the roleplay.",

        "company_q": "Target company:",
        "company_placeholder": "e.g. Uber, Mercado Libre, Nubank",
        "company_required": "Please enter a company name.",

        "role_q": "Select Alex's role:",
        "other_role_option": "Other",
        "custom_role_q": "Enter custom role:",
        "role_required": "Please enter a valid role.",
        "role_info_message": "Please make the role precise and unambiguous to ensure a better roleplay.",

        "start_btn": "Start Simulation",
        "reset_btn": "Reset Session",

        "greeting": "Hello. I am Alex. I have 2 minutes, what is this about?",

        # Instructions
        "instructions_label": "Instructions",
        "instructions": [
            "1. Click record to say your message to Alex (max 1 min).",
            "2. Say 'Stop simulation' to finish and get your feedback."
        ],
        "stop_phrase": "Stop simulation",

        # Audio
        "listening": "Listening...",
        "input_label": "Speak to Alex:",
        "no_audio_heard": "I couldn't hear you clearly. Could you repeat that?",
        "audio_invalid": "System Note: The audio recording exceeds the 60-second limit or is invalid.",

        # Errors
        "busy_server": "Server busy. Please try again in a minute.",
        "no_ai_response": "I did not receive a response from Alex. Please try again.",

        # Feedback
        "feedback_intro": "Simulation finished. Analysis:",
        "debug_label": "🎙️ Listen to your last recording",

        # PDF
        "pdf_uploader_label": "Optional: Upload company research (PDF)",
        "pdf_info": "If you upload a PDF, Alex will use it to better understand the company's context.",
        "url_input_label": "Optional: Paste the company website URL",
        "pdf_processing": "Processing PDF...",
        "pdf_empty": "Could not extract readable text from the uploaded PDF.",

        # Assistant
        "assistant_title": "Sales Assistant",
        "assistant_subtitle": "Live help during the roleplay",
        "assistant_input": "Ask for guidance based on the live conversation and FY26 materials",
        "assistant_placeholder": "e.g. How should I position GCP here?",
        "assistant_button": "Ask Assistant",
        "assistant_sources": "Sources used:",
        "assistant_empty_state": "Ask about positioning, discovery, objections, next steps, or FY26 plays.",
        "assistant_loading": "Thinking...",
        "assistant_error": "Error in sales assistant:",
        "assistant_connected": "Internal FY26 knowledge connected",

        # UI Sections
        "roleplay_header": "Live Customer Roleplay",
        "roleplay_subtitle": "Simulate a real enterprise sales conversation with a time-constrained executive.",
        "roleplay_tip": "Simulate a cold call with a skeptical prospect. You must connect your pitch to the company and present at least 3 GCP products.",

        "scenario_preview": "Scenario Preview",
        "scenario_subtitle": "Preview of the simulation context.",

        "company": "Company",
        "role": "Role",
        "language": "Language",
        "additional_context": "Additional Context",
        "presentation_language": "Presentation Language",

        "profile_kicker": "Profile",
        "scenario_kicker": "Scenario",

        # Assistant UI
        "assistant_info": "The Sales Assistant is grounded in FY26 plays, battle cards, uploaded PDF research, and the live roleplay transcript.",
        "assistant_tip": "Use this pane as your live copilot.",

        # Misc
        "knowledge_badge_title": "FY26 Sales Knowledge",
        "knowledge_badge_desc": "Connected to official Plays & Battle Cards",
        "no_docs_loaded": "No FY26 internal documents were loaded from GCS.",
        "session_caption": "Live simulation with Alex",
        "simulator_info": "This simulator recreates enterprise sales conversations and provides real-time guidance."
    },

    "Spanish": {
        # Setup
        "setup_title": "Configuración del Roleplay",
        "setup_subtitle": "Configura el buyer persona, el contexto de la cuenta y los insumos antes de iniciar la simulación.",

        "company_q": "Empresa objetivo:",
        "company_placeholder": "Ej: Uber, Mercado Libre, Nubank",
        "company_required": "Por favor ingresa una empresa.",

        "role_q": "Selecciona el rol de Alex:",
        "other_role_option": "Otro",
        "custom_role_q": "Ingresa el rol:",
        "role_required": "Por favor ingresa un rol válido.",
        "role_info_message": "Haz que el rol sea preciso y claro para lograr un mejor roleplay.",

        "start_btn": "Iniciar Simulación",
        "reset_btn": "Reiniciar Sesión",

        "greeting": "Hola. Soy Alex. Tengo 2 minutos, ¿de qué se trata esto?",

        # Instructions
        "instructions_label": "Instrucciones",
        "instructions": [
            "1. Haz clic en grabar para decir tu mensaje a Alex (máx. 1 min).",
            "2. Di 'Detener simulación' para terminar y recibir tu feedback."
        ],
        "stop_phrase": "Detener simulación",

        # Audio
        "listening": "Escuchando...",
        "input_label": "Habla con Alex:",
        "no_audio_heard": "No pude escucharte bien. ¿Podrías repetir?",
        "audio_invalid": "Nota del sistema: la grabación de audio excede el límite de 60 segundos o es inválida.",

        # Errors
        "busy_server": "Servidor ocupado. Por favor, intenta de nuevo en un minuto.",
        "no_ai_response": "No recibí una respuesta de Alex. Por favor, intenta de nuevo.",

        # Feedback
        "feedback_intro": "Simulación finalizada. Análisis:",
        "debug_label": "🎙️ Escucha tu última grabación",

        # PDF
        "pdf_uploader_label": "Opcional: Sube investigación de la empresa (PDF)",
        "pdf_info": "Si subes un PDF, Alex lo usará para entender mejor el contexto de la empresa.",
        "url_input_label": "Opcional: Pega la URL del sitio web de la empresa",
        "pdf_processing": "Procesando PDF...",
        "pdf_empty": "No se pudo extraer texto legible del PDF cargado.",

        # Assistant
        "assistant_title": "Sales Assistant",
        "assistant_subtitle": "Ayuda en vivo durante el roleplay",
        "assistant_input": "Pide orientación con base en la conversación en vivo y en los materiales FY26",
        "assistant_placeholder": "Ej: ¿Cómo debería posicionar GCP aquí?",
        "assistant_button": "Preguntar al Assistant",
        "assistant_sources": "Fuentes utilizadas:",
        "assistant_empty_state": "Pregunta por posicionamiento, discovery, objeciones, próximos pasos o plays FY26.",
        "assistant_loading": "Pensando...",
        "assistant_error": "Error en el asistente de ventas:",
        "assistant_connected": "Conocimiento interno FY26 conectado",

        # UI Sections
        "roleplay_header": "Roleplay de cliente en vivo",
        "roleplay_subtitle": "Simula una conversación real de ventas enterprise con un ejecutivo con poco tiempo.",
        "roleplay_tip": "Simula una cold call con un prospecto escéptico. Debes conectar tu pitch con la empresa y presentar al menos 3 productos de GCP.",

        "scenario_preview": "Vista previa del escenario",
        "scenario_subtitle": "Vista previa del contexto de la simulación.",

        "company": "Empresa",
        "role": "Rol",
        "language": "Idioma",
        "additional_context": "Contexto adicional",
        "presentation_language": "Idioma de presentación",

        "profile_kicker": "Perfil",
        "scenario_kicker": "Escenario",

        # Assistant UI
        "assistant_info": "El Sales Assistant se apoya en plays FY26, battle cards, investigación en PDF cargada y la transcripción del roleplay en vivo.",
        "assistant_tip": "Usa este panel como tu copiloto en vivo.",

        # Misc
        "knowledge_badge_title": "Conocimiento de Ventas FY26",
        "knowledge_badge_desc": "Conectado a Plays y Battle Cards oficiales",
        "no_docs_loaded": "No se cargaron documentos internos FY26 desde GCS.",
        "session_caption": "Simulación en vivo con Alex",
        "simulator_info": "Este simulador recrea conversaciones de ventas enterprise y ofrece guía en tiempo real."
    },

    "Portuguese": {
        # Setup
        "setup_title": "Configuração do Roleplay",
        "setup_subtitle": "Configure a persona do comprador, o contexto da conta e os insumos antes de iniciar a simulação.",

        "company_q": "Empresa alvo:",
        "company_placeholder": "Ex: Uber, Mercado Livre, Nubank",
        "company_required": "Digite o nome de uma empresa.",

        "role_q": "Selecione o papel de Alex:",
        "other_role_option": "Outro",
        "custom_role_q": "Digite o papel:",
        "role_required": "Digite um papel válido.",
        "role_info_message": "Torne o papel preciso e claro para garantir um roleplay melhor.",

        "start_btn": "Iniciar Simulação",
        "reset_btn": "Reiniciar Sessão",

        "greeting": "Olá. Sou Alex. Tenho 2 minutos, do que se trata isso?",

        # Instructions
        "instructions_label": "Instruções",
        "instructions": [
            "1. Clique em gravar para dizer sua mensagem a Alex (máx. 1 min).",
            "2. Diga 'Parar simulação' para encerrar e receber seu feedback."
        ],
        "stop_phrase": "Parar simulação",

        # Audio
        "listening": "Ouvindo...",
        "input_label": "Fale com Alex:",
        "no_audio_heard": "Não consegui ouvir você claramente. Poderia repetir?",
        "audio_invalid": "Nota do sistema: a gravação de áudio excede o limite de 60 segundos ou é inválida.",

        # Errors
        "busy_server": "Servidor ocupado. Tente novamente em um minuto.",
        "no_ai_response": "Não recebi uma resposta de Alex. Tente novamente.",

        # Feedback
        "feedback_intro": "Simulação finalizada. Análise:",
        "debug_label": "🎙️ Ouça sua última gravação",

        # PDF
        "pdf_uploader_label": "Opcional: Envie pesquisa da empresa (PDF)",
        "pdf_info": "Se você enviar um PDF, Alex o usará para entender melhor o contexto da empresa.",
        "url_input_label": "Opcional: Cole a URL do site da empresa",
        "pdf_processing": "Processando PDF...",
        "pdf_empty": "Não foi possível extrair texto legível do PDF enviado.",

        # Assistant
        "assistant_title": "Sales Assistant",
        "assistant_subtitle": "Ajuda ao vivo durante o roleplay",
        "assistant_input": "Peça orientação com base na conversa ao vivo e nos materiais FY26",
        "assistant_placeholder": "Ex: Como devo posicionar GCP aqui?",
        "assistant_button": "Perguntar ao Assistant",
        "assistant_sources": "Fontes usadas:",
        "assistant_empty_state": "Pergunte sobre posicionamento, discovery, objeções, próximos passos ou plays FY26.",
        "assistant_loading": "Pensando...",
        "assistant_error": "Erro no assistente de vendas:",
        "assistant_connected": "Conhecimento interno FY26 conectado",

        # UI Sections
        "roleplay_header": "Roleplay de cliente ao vivo",
        "roleplay_subtitle": "Simule uma conversa real de vendas enterprise com um executivo com pouco tempo.",
        "roleplay_tip": "Simule uma cold call com um prospect cético. Você deve conectar seu pitch à empresa e apresentar pelo menos 3 produtos de GCP.",

        "scenario_preview": "Prévia do cenário",
        "scenario_subtitle": "Prévia do contexto da simulação.",

        "company": "Empresa",
        "role": "Papel",
        "language": "Idioma",
        "additional_context": "Contexto adicional",
        "presentation_language": "Idioma de apresentação",

        "profile_kicker": "Perfil",
        "scenario_kicker": "Cenário",

        # Assistant UI
        "assistant_info": "O Sales Assistant é baseado em plays FY26, battle cards, pesquisa em PDF enviada e na transcrição do roleplay ao vivo.",
        "assistant_tip": "Use este painel como seu copiloto ao vivo.",

        # Misc
        "knowledge_badge_title": "Conhecimento de Vendas FY26",
        "knowledge_badge_desc": "Conectado a Plays e Battle Cards oficiais",
        "no_docs_loaded": "Nenhum documento interno FY26 foi carregado do GCS.",
        "session_caption": "Simulação ao vivo com Alex",
        "simulator_info": "Este simulador recria conversas de vendas enterprise e oferece orientação em tempo real."
    }
}