J1QL_SKIP_COUNT = 250
J1QL_LIMIT_COUNT = 250

QUERY_V1 = """
  query J1QL($query: String!, $variables: JSON, $dryRun: Boolean, $includeDeleted: Boolean) {
    queryV1(query: $query, variables: $variables, dryRun: $dryRun, includeDeleted: $includeDeleted) {
      type
      data
    }
  }
"""

CURSOR_QUERY_V1 = """
  query J1QL_v2($query: String!, $variables: JSON, $flags: QueryV1Flags, $includeDeleted: Boolean, $cursor: String) {
    queryV1(
      query: $query
      variables: $variables
      deferredResponse: DISABLED
      flags: $flags
      includeDeleted: $includeDeleted
      cursor: $cursor
    ) {
      type
      data
      cursor
      __typename
    }
  }
"""

CREATE_ENTITY = """
  mutation CreateEntity(
    $entityKey: String!
    $entityType: String!
    $entityClass: [String!]!
    $properties: JSON
  ) {
    createEntity(
      entityKey: $entityKey
      entityType: $entityType
      entityClass: $entityClass
      properties: $properties
    ) {
      entity {
        _id
      }
      vertex {
        id
        entity {
          _id
        }
      }
    }
  }
"""

DELETE_ENTITY = """
  mutation DeleteEntity($entityId: String!, $timestamp: Long) {
    deleteEntity(entityId: $entityId, timestamp: $timestamp) {
      entity {
        _id
      }
      vertex {
        id
        entity {
          _id
        }
        properties
      }
    }
  }
"""

UPDATE_ENTITY = """
  mutation UpdateEntity($entityId: String!, $properties: JSON) {
    updateEntity(entityId: $entityId, properties: $properties) {
      entity {
        _id
      }
      vertex {
        id
      }
    }
  }
"""

CREATE_RELATIONSHIP = """
  mutation CreateRelationship(
    $relationshipKey: String!
    $relationshipType: String!
    $relationshipClass: String!
    $fromEntityId: String!
    $toEntityId: String!
    $properties: JSON
  ) {
    createRelationship(
      relationshipKey: $relationshipKey
      relationshipType: $relationshipType
      relationshipClass: $relationshipClass
      fromEntityId: $fromEntityId
      toEntityId: $toEntityId
      properties: $properties
    ) {
      relationship {
        _id
      }
      edge {
        id
        toVertexId
        fromVertexId
        relationship {
          _id
        }
        properties
      }
    }
  }
"""

UPDATE_RELATIONSHIP = """
      mutation UpdateRelationship (
      $relationshipId: String!
      $timestamp: Long
      $properties: JSON
    ) {
      updateRelationship (
        relationshipId: $relationshipId,
        timestamp: $timestamp,
        properties: $properties
      ) {
        relationship {
          _id
          ...
        }
        edge {
          id
          toVertexId
          fromVertexId
          relationship {
            _id
            ...
          }
          properties
        }
      }
    }
"""

DELETE_RELATIONSHIP = """
  mutation DeleteRelationship($relationshipId: String! $timestamp: Long) {
    deleteRelationship (relationshipId: $relationshipId, timestamp: $timestamp) {
      relationship {
        _id
      }
      edge {
        id
        toVertexId
        fromVertexId
        relationship {
          _id
        }
        properties
      }
    }
  }
"""

CREATE_INSTANCE = """
    mutation CreateInstance($instance: CreateIntegrationInstanceInput!) {
        createIntegrationInstance(instance: $instance) {
            id
            name
            accountId
            pollingInterval
            integrationDefinitionId
            description
            config
        }
    }
"""

ALL_PROPERTIES = """
    query getAllAssetProperties {
      getAllAssetProperties
    }
"""

CREATE_SMARTCLASS = """
    mutation CreateSmartClass($input: CreateSmartClassInput!) {
      createSmartClass(input: $input) {
        id
        accountId
        tagName
        description
        ruleId
        __typename
      }
    }
"""

CREATE_SMARTCLASS_QUERY = """
    mutation CreateSmartClassQuery($input: CreateSmartClassQueryInput!) {
      createSmartClassQuery(input: $input) {
        id
        smartClassId
        description
        query
        __typename
      }
    }
"""

EVALUATE_SMARTCLASS = """
    mutation EvaluateSmartClassRule($smartClassId: ID!) {
      evaluateSmartClassRule(smartClassId: $smartClassId) {
        ruleId
        __typename
      }
    }
"""

GET_SMARTCLASS_DETAILS = """
    query GetSmartClass($id: ID!) {
        smartClass(id: $id) {
          id
          accountId
          tagName
          description
          ruleId
        queries {
          id
          smartClassId
          description
          query
          __typename
        }
        tags {
          id
          smartClassId
          name
          type
          value
          __typename
        }
        rule {
          lastEvaluationEndOn
          evaluationStep
          __typename
        }
        __typename
        }
    }
"""

INTEGRATION_JOB_VALUES = """
    query IntegrationJobs(
      $status: IntegrationJobStatus
      $integrationInstanceId: String
      $integrationDefinitionId: String
      $integrationInstanceIds: [String]
      $cursor: String
      $size: Int
    ) {
      integrationJobs(
        status: $status
        integrationInstanceId: $integrationInstanceId
        integrationDefinitionId: $integrationDefinitionId
        integrationInstanceIds: $integrationInstanceIds
        cursor: $cursor
        size: $size
      ) {
        jobs {
          id
          status
          integrationInstanceId
          createDate
          endDate
          hasSkippedSteps
          integrationInstance {
            id
            name
            __typename
          }
          integrationDefinition {
            id
            title
            integrationType
            __typename
          }
          __typename
        }
        pageInfo {
          endCursor
          __typename
        }
        __typename
      }
    }
"""

INTEGRATION_INSTANCE_EVENT_VALUES = """
    query ListEvents(
      $jobId: String!
      $integrationInstanceId: String!
      $cursor: String
      $size: Int
    ) {
      integrationEvents(
        size: $size
        cursor: $cursor
        jobId: $jobId
        integrationInstanceId: $integrationInstanceId
      ) {
        events {
          id
          name
          description
          createDate
          jobId
          level
          eventCode
          __typename
        }
        pageInfo {
          endCursor
          hasNextPage
          __typename
        }
        __typename
      }
    }
"""

LIST_RULE_INSTANCES = """
    query listRuleInstances(
        $limit: Int, 
        $cursor: String, 
        $filters: ListRuleInstancesFilters) {
      listRuleInstances(
        limit: $limit, 
        cursor: $cursor, 
        filters: $filters) {
        questionInstances {
          ...RuleInstanceFields
          __typename
        }
        pageInfo {
          hasNextPage
          endCursor
          __typename
        }
        __typename
      }
    }

    fragment RuleInstanceFields on QuestionRuleInstance {
      id
      accountId
      name
      description
      version
      lastEvaluationStartOn
      lastEvaluationEndOn
      evaluationStep
      specVersion
      notifyOnFailure
      triggerActionsOnNewEntitiesOnly
      pollingInterval
      templates
      outputs
      question {
        queries {
          query
          name
          version
          includeDeleted
          __typename
        }
        __typename
      }
      questionId
      latest
      deleted
      type
      operations {
        when
        actions
        __typename
      }
      latestAlertId
      latestAlertIsActive
      state {
        actions
        __typename
      }
      tags
      remediationSteps
      __typename
    }
"""

J1QL_FROM_NATURAL_LANGUAGE = """
    query j1qlFromNaturalLanguage($input: J1qlFromNaturalLanguageInput!) {
        j1qlFromNaturalLanguage(input: $input) {
            j1ql
        }
    }
"""