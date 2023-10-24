
## 中文

### Condense Prompt

鉴于以下对话和后续问题，将后续问题改写为
是一个独立的问题，用其原始语言。确保避免使用任何不清楚的代词。
Chat History:
{chat_history}
接下来的提问: {question}
转化后的问题:

### Conversation QA Prompt

使用以下上下文来回答最后的问题。
                如果你不知道答案，就说你不知道，不要试图编造答案。
                最多使用三个句子，并尽可能保持答案简洁。
                总是说“谢谢您的提问！”在答案的开头。始终在答案中返回“来源”部分。 
                {context}
                问题: {question}
                我的答案是:

### QA Prompt

下面将给你一个“问题”和一些“已知信息”，请判断这个“问题”是否可以从“已知信息”中得到答案。
                若可以从“已知信息”中获取答案，请直接输出答案。
                若不可以从“已知信息”中获取答案，请回答“根据已知信息无法回答”。ALWAYS return a "SOURCE" part in your answer from.

                 ==================================== 
                已知信息:
                {summaries}
                ====================================
                问题：
                {question}
                ====================================
                 AI:
                 Sources
## 葡萄牙语

### Condense Prompt

Dada a seguinte conversa e perguntas de acompanhamento, reformule a pergunta de acompanhamento como
é uma questão separada, em seu idioma original. Certifique-se de evitar o uso de pronomes pouco claros.
Histórico de conversa:
{chat_history}
Próxima pergunta: {question}
Perguntas após a conversão:

### Conversation QA Prompt

Use o seguinte contexto para responder à pergunta final.
Se você não sabe a resposta, apenas diga que não sabe e não tente inventar a resposta.
Use no máximo três frases e mantenha suas respostas o mais concisas possível.
Sempre diga “Obrigado por perguntar!” no início da sua resposta. Sempre retorne a seção "Fonte" em sua resposta.
{context}
Pergunta: {question}
Minha resposta é:

### QA Prompt

Você receberá uma "pergunta" e algumas "informações conhecidas" abaixo. Por favor, julgue se a resposta a esta "pergunta" pode ser obtida a partir das "informações conhecidas".
Se a resposta puder ser obtida a partir de "informações conhecidas", envie a resposta diretamente.
Se a resposta não puder ser obtida a partir de “informações conhecidas”, responda “Incapaz de responder com base em informações conhecidas”. SEMPRE retorne uma parte "FONTE" em sua resposta.

 ===================================
Informações conhecidas:
{summaries}
===================================
pergunta:
{question}
===================================
 IA:
 Fontes