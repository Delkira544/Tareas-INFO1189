"""
Schema GraphQL principal
Combina las queries y mutations en un schema unificado
"""
import strawberry
from .resolvers import Query, Mutation


# Crear el schema GraphQL combinando Query y Mutation
schema = strawberry.Schema(query=Query, mutation=Mutation)
