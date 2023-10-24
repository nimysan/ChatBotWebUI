from langchain.document_loaders import Docx2txtLoader

import tempfile

temp = tempfile.NamedTemporaryFile()
print(temp)
print(temp.name)


# loader = Docx2txtLoader('/Users/yexw/accounts/supernet/RAG项目推进/FAQ+Youcine.docx')
# loaded_documents = loader.load()
# print(f"tje doc is {loaded_documents}")