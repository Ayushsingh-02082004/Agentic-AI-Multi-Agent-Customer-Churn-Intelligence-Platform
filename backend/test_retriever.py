from backend.vectorstore.retriever import Retriever

retriever = Retriever()

result = retriever.retrieve(
    "customers likely to churn"
)

print(result)