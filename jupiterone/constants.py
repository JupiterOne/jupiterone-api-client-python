J1QL_SKIP_COUNT = 250
J1QL_LIMIT_COUNT = 250

# GRAPH
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
  mutation DeleteEntity($entityId: String!, $timestamp: Long, $hardDelete: Boolean) {
    deleteEntityV2(
      entityId: $entityId
      timestamp: $timestamp
      hardDelete: $hardDelete
    ) {
      entity
      __typename
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
UPDATE_RELATIONSHIPV2 = """
mutation UpdateRelationshipV2 (
  $relationship: JSON!
  $timestamp: Long
) {
  updateRelationshipV2 (
    relationship: $relationship,
    timestamp: $timestamp,
  ) {
    relationship
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

# ENTITIES
ALL_PROPERTIES = """
    query getAllAssetProperties {
      getAllAssetProperties
    }
"""
GET_ENTITY_RAW_DATA = """
    query GetEntityRawData ($entityId: String!, $source: String!,
        )   {
        entityRawDataLegacy(entityId: $entityId, , source: $source) {
            entityId
            payload {
                ... on RawDataJSONEntityLegacy {
                    contentType
                    name
                    data
                }
            }    
        }
    }
"""

# SMART CLASSES
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

# INTEGRATIONS
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
FIND_INTEGRATION_DEFINITION = """
    query FindIntegrationDefinition($integrationType: String!, $includeConfig: Boolean!) {
      findIntegrationDefinition(integrationType: $integrationType) {
        ...IntegrationDefinitionsValues
        __typename
      }
    }

    fragment IntegrationDefinitionsValues on IntegrationDefinition {
      id
      name
      type
      title
      displayMode
      oAuth {
        oAuthUrlGeneratorPath
        __typename
      }
      offsiteUrl
      offsiteButtonTitle
      offsiteStatusQuery
      integrationType
      integrationClass
      integrationCategory
      beta
      docsWebLink
      repoWebLink
      invocationPaused
      managedExecutionDisabled
      integrationPlatformFeatures {
        supportsChildInstances
        supportsCollectors
        supportsIngestionSourcesConfig
        __typename
      }
      ingestionSourcesConfig {
        id
        title
        description
        defaultsToDisabled
        childIngestionSourcesMetadata {
          id
          name
          __typename
        }
        cannotBeDisabled
        __typename
      }
      ingestionSourcesOverrides {
        enabled
        ingestionSourceId
        __typename
      }
      totalInstanceCount
      integrationJobStatusMetrics {
        count
        status
        __typename
      }
      ...IntegrationDefinitionConfigFragment @include(if: $includeConfig)
      __typename
    }

    fragment IntegrationDefinitionConfigFragment on IntegrationDefinition {
      configFields {
        ...ConfigFieldsRecursive
        __typename
      }
      authSections {
        id
        description
        displayName
        configFields {
          ...ConfigFieldsRecursive
          __typename
        }
        verificationDisabled
        __typename
      }
      configSections {
        displayName
        configFields {
          ...ConfigFieldsRecursive
          __typename
        }
        __typename
      }
      __typename
    }

    fragment ConfigFieldsRecursive on ConfigField {
      ...ConfigFieldValues
      configFields {
        ...ConfigFieldValues
        configFields {
          ...ConfigFieldValues
          __typename
        }
        __typename
      }
      __typename
    }

    fragment ConfigFieldValues on ConfigField {
      key
      displayName
      description
      type
      format
      defaultValue
      helperText
      inputAdornment
      mask
      optional
      immutable
      readonly
      computed
      options {
        value
        description
        label
        webLink
        default
        __typename
      }
      __typename
    }
"""
INTEGRATION_INSTANCES = """
    fragment IntegrationInstanceLiteValues on IntegrationInstanceLite {
      id
      name
      accountId
      sourceIntegrationInstanceId
      pollingInterval
      pollingIntervalCronExpression {
        hour
        dayOfWeek
        __typename
      }
      integrationDefinitionId
      description
      config
      instanceRelationship
      mostRecentJob {
        status
        hasSkippedSteps
        createDate
        __typename
      }
      __typename
    }

    query IntegrationInstances($definitionId: String, $cursor: String, $limit: Int, $filter: ListIntegrationInstancesSearchFilter) {
      integrationInstancesV2(
        definitionId: $definitionId
        cursor: $cursor
        limit: $limit
        filter: $filter
      ) {
        instances {
          ...IntegrationInstanceLiteValues
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
INTEGRATION_INSTANCE = """
    fragment IntegrationInstanceValues on IntegrationInstance {
      id
      name
      accountId
      sourceIntegrationInstanceId
      pollingInterval
      pollingIntervalCronExpression {
        hour
        dayOfWeek
        __typename
      }
      integrationDefinition {
        name
        integrationType
        __typename
      }
      integrationDefinitionId
      description
      config
      offsiteComplete
      jobs {
        jobs {
          ...IntegrationInstanceJobValues
          __typename
        }
        __typename
      }
      instanceRelationship
      ingestionSourcesOverrides {
        ingestionSourceId
        enabled
        __typename
      }
      collectorPoolId
      __typename
    }

    fragment IntegrationInstanceJobValues on IntegrationJob {
      id
      status
      integrationInstanceId
      createDate
      endDate
      hasSkippedSteps
      __typename
    }

    query IntegrationInstance($integrationInstanceId: String!) {
      integrationInstance(id: $integrationInstanceId) {
        ...IntegrationInstanceValues
        __typename
      }
    }
"""
UPDATE_INTEGRATION_INSTANCE = """
    mutation UpdateIntegrationInstance($id: String!, $update: UpdateIntegrationInstanceInput!) {
      updateIntegrationInstance(id: $id, update: $update) {
        id
        name
        pollingInterval
        pollingIntervalCronExpression {
          hour
          dayOfWeek
          __typename
        }
        integrationDefinitionId
        description
        config
        offsiteComplete
        ingestionSourcesOverrides {
          ingestionSourceId
          enabled
          __typename
        }
        collectorPoolId
        __typename
      }
    }
"""

# J1QL & AI
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
DEFERRED_RESPONSE_QUERY = """
query J1QL(
  $query: String!
  $variables: JSON
  $cursor: String
  $deferredResponse: DeferredResponseOption
) {
  queryV1(
    query: $query
    variables: $variables
    deferredResponse: $deferredResponse
    cursor: $cursor
  ) {
    type
    url
  }
}
"""
J1QL_FROM_NATURAL_LANGUAGE = """
    query j1qlFromNaturalLanguage($input: J1qlFromNaturalLanguageInput!) {
        j1qlFromNaturalLanguage(input: $input) {
            j1ql
        }
    }
"""

# ALERT RULES
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
CREATE_RULE_INSTANCE = """
    mutation createInlineQuestionRuleInstance($instance: CreateInlineQuestionRuleInstanceInput!) {
      createInlineQuestionRuleInstance(instance: $instance) {
        ...RuleInstanceFields
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
      ignorePreviousResults
      pollingInterval
      templates
      outputs
      labels {
        labelName
        labelValue
        __typename
      }
      question {
        queries {
          query
          name
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
DELETE_RULE_INSTANCE = """
    mutation deleteRuleInstance($id: ID!) {
      deleteRuleInstance(id: $id) {
        id
        __typename
      }
    }
"""
UPDATE_RULE_INSTANCE = """
    mutation updateQuestionRuleInstance($instance: UpdateInlineQuestionRuleInstanceInput!) {
      updateInlineQuestionRuleInstance(instance: $instance) {
        ...RuleInstanceFields
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
      ignorePreviousResults
      pollingInterval
      templates
      outputs
      labels {
        labelName
        labelValue
        __typename
      }
      question {
        queries {
          query
          name
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
EVALUATE_RULE_INSTANCE = """
    mutation evaluateRuleInstance($id: ID!) {
      evaluateRuleInstance(id: $id) {
        id
        __typename
      }
    }
"""
LIST_COLLECTION_RESULTS = """
    query listCollectionResults($collectionType: CollectionType!, 
        $collectionOwnerId: String!, 
        $beginTimestamp: Long!, 
        $endTimestamp: Long!, 
        $limit: Int, 
        $cursor: String, 
        $tag: String) {
          listCollectionResults(
            collectionType: $collectionType
            collectionOwnerId: $collectionOwnerId
            beginTimestamp: $beginTimestamp
            endTimestamp: $endTimestamp
            limit: $limit
            cursor: $cursor
            tag: $tag
          ) {
            results {
              accountId
              collectionOwnerId
              collectionOwnerVersion
              collectionType
              outputs {
                name
                value
                __typename
              }
              rawDataDescriptors {
                name
                persistedResultType
                rawDataKey
                recordCount
                recordCreateCount
                recordDeleteCount
                recordUpdateCount
                __typename
              }
              tag
              timestamp
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
GET_RAW_DATA_DOWNLOAD_URL = """
    query getRawDataDownloadUrl(
                $rawDataKey: String!
            ) {
              getRawDataDownloadUrl(
                rawDataKey: $rawDataKey)
            }
"""

# QUESTIONS & COMPLIANCE
QUESTIONS = """
    query questions($searchQuery: String, $integrationDefinitionId: String, $tags: [String], $type: ListQuestionsType, $limit: Int, $cursor: String, $categories: [String]) {
      questions(
        searchQuery: $searchQuery
        integrationDefinitionId: $integrationDefinitionId
        tags: $tags
        type: $type
        limit: $limit
        cursor: $cursor
        categories: $categories
      ) {
        questions {
          ...QuestionFields
          __typename
        }
        totalHits
        pageInfo {
          endCursor
          hasNextPage
          __typename
        }
        __typename
      }
    }

    fragment QuestionFields on Question {
      id
      sourceId
      title
      description
      tags
      lastUpdatedTimestamp
      queries {
        name
        query
        version
        resultsAre
        __typename
      }
      compliance {
        standard
        requirements
        controls
        __typename
      }
      variables {
        name
        required
        default
        __typename
      }
      accountId
      integrationDefinitionId
      showTrend
      pollingInterval
      __typename
    }
"""

GET_QUESTION = """
    query question($id: ID!) {
      question(id: $id) {
        ...QuestionFields
        __typename
      }
    }

    fragment QuestionFields on Question {
      id
      sourceId
      title
      description
      tags
      lastUpdatedTimestamp
      queries {
        name
        query
        version
        resultsAre
        __typename
      }
      compliance {
        standard
        requirements
        controls
        __typename
      }
      variables {
        name
        required
        default
        __typename
      }
      accountId
      integrationDefinitionId
      showTrend
      pollingInterval
      __typename
    }
"""
CREATE_QUESTION = """
    mutation CreateQuestion($question: CreateQuestionInput!) {
        createQuestion(question: $question) {
            id
            title
            description
            tags
            queries {
                name
                query
                version
                resultsAre
                __typename
            }
            compliance {
                standard
                requirements
                controls
                __typename
            }
            variables {
                name
                required
                default
                __typename
            }
            accountId
            integrationDefinitionId
            showTrend
            pollingInterval
            lastUpdatedTimestamp
            __typename
        }
    }
"""
COMPLIANCE_FRAMEWORK_ITEM = """
query complianceFrameworkItem($input: ComplianceFrameworkItemInput!) {
  complianceFrameworkItem(input: $input) {
    ...ComplianceFrameworkItemFields
    __typename
  }
}

fragment ComplianceFrameworkItemFields on ComplianceFrameworkItem {
  id
  frameworkId
  name
  description
  displayCategory
  ref
  evaluationProgress
  applicabilityReason
  lastEvaluationTimestamp
  evaluationResult
  auditStatus
  groupId
  webLink
  summary {
    id
    hasLinkedPolicyItem
    evidenceCollectionSummary {
      id
      hasEvidence
      hasInternalEvidenceCollected
      hasExternalEvidenceAttached
      questionnaireAnswer
      __typename
    }
    __typename
  }
  libraryItems {
    inheritedEvidenceLibraryItems {
      ...ComplianceLibraryItemWithLinkedPolicyItemFields
      frameworkItemMetadatas {
        id
        name
        frameworkId
        __typename
      }
      evidence {
        ...ComplianceLibraryItemEvidenceFields
        __typename
      }
      __typename
    }
    ignoredEvidenceLibraryItems {
      ...ComplianceLibraryItemWithLinkedPolicyItemFields
      __typename
    }
    __typename
  }
  evidence {
    notes {
      ...ComplianceNoteFields
      __typename
    }
    links {
      ...ComplianceLinkFields
      __typename
    }
    questionnaireAnswer {
      ...ComplianceQuestionnaireAnswerFields
      __typename
    }
    externalUploadEvidences {
      ...ExternalUploadEvidenceFields
      __typename
    }
    questionEvaluations {
      ...QuestionEvaluationFields
      __typename
    }
    __typename
  }
  reviewConfiguration {
    ...ReviewConfigurationFields
    __typename
  }
  __typename
}

fragment ComplianceLibraryItemWithLinkedPolicyItemFields on ComplianceLibraryItem {
  ...ComplianceLibraryItemMetadataFields
  linkedPolicyItem {
    id
    ref
    name
    isAdopted
    linkedPolicy {
      id
      ref
      name
      __typename
    }
    __typename
  }
  __typename
}

fragment ComplianceLibraryItemMetadataFields on ComplianceLibraryItem {
  id
  name
  description
  displayCategory
  policyItemId
  ref
  evaluationProgress
  evaluationResult
  lastEvaluationTimestamp
  webLink
  __typename
}

fragment ComplianceLibraryItemEvidenceFields on ComplianceLibraryItemEvidence {
  notes {
    ...ComplianceNoteFields
    __typename
  }
  links {
    ...ComplianceLinkFields
    __typename
  }
  externalUploadEvidences {
    ...ExternalUploadEvidenceFields
    __typename
  }
  questionEvaluations {
    ...QuestionEvaluationFields
    __typename
  }
  allEvidence {
    id
    evidenceType
    lastUpdatedTimestamp
    ... on ComplianceQuestionEvaluation {
      questionId
      evaluationResult
      results {
        name
        query
        rawResultKey
        recordCount
        __typename
      }
      __typename
    }
    ... on ComplianceNote {
      creatorUserId
      body
      createTimestamp
      name
      __typename
    }
    ... on ComplianceLink {
      creatorUserId
      description
      linkUrl
      createTimestamp
      name
      __typename
    }
    ... on ExternalUploadEvidence {
      lastUpdatedTimestamp
      creatorUserId
      body
      externalUploadId
      externalUpload {
        id
        creatorUserId
        isUploadComplete
        filename
        name
        s3ObjectKey
        lastUpdatedTimestamp
        expirationTimestamp
        __typename
      }
      createTimestamp
      __typename
    }
    __typename
  }
  __typename
}

fragment ComplianceNoteFields on ComplianceNote {
  id
  evidenceType
  creatorUserId
  createTimestamp
  lastUpdatedTimestamp
  body
  name
  __typename
}

fragment ComplianceLinkFields on ComplianceLink {
  id
  evidenceType
  creatorUserId
  createTimestamp
  lastUpdatedTimestamp
  description
  linkUrl
  name
  __typename
}

fragment ExternalUploadEvidenceFields on ExternalUploadEvidence {
  id
  evidenceType
  creatorUserId
  createTimestamp
  lastUpdatedTimestamp
  body
  externalUploadId
  externalUpload {
    id
    creatorUserId
    isUploadComplete
    filename
    name
    s3ObjectKey
    lastUpdatedTimestamp
    expirationTimestamp
    __typename
  }
  __typename
}

fragment QuestionEvaluationFields on ComplianceQuestionEvaluation {
  id
  frameworkItemId
  questionId
  results {
    name
    query
    rawResultKey
    recordCount
    __typename
  }
  lastUpdatedTimestamp
  evidenceType
  evaluationResult
  __typename
}

fragment ComplianceQuestionnaireAnswerFields on ComplianceQuestionnaireAnswer {
  id
  evidenceType
  creatorUserId
  createTimestamp
  lastUpdatedTimestamp
  body
  answer
  __typename
}

fragment ReviewConfigurationFields on ComplianceReviewConfiguration {
  id
  ownerUserIds
  reviewFrequency
  nextDueDateTimestamp
  lastDueDateTimestamp
  currentReviewCompletedOnTimestamp
  currentReviewCompletedBy
  lastReviewCompletedOnTimestamp
  lastReviewCompletedBy
  __typename
}
"""

# PARAMETERS
PARAMETER = """
    query Query($name: String!) {
      parameter(name: $name) {
        name
        value
        secret
        lastUpdatedOn
      }
    }
"""
PARAMETER_LIST = """
    query Query($limit: Int, $cursor: String) {
      parameterList(limit: $limit, cursor: $cursor) {
        items {
          name
          value
          secret
          lastUpdatedOn
        }
        pageInfo {
          endCursor
          hasNextPage
        }
      }
    }
"""
UPSERT_PARAMETER = """
    mutation UpsertParameter($name: String!, $value: ParameterValue!, $secret: Boolean) {
      setParameter(name: $name, value: $value, secret: $secret) {
        success
        __typename
      }
    }
"""
UPDATE_ENTITYV2 = """
    mutation UpdateEntityV2($timestamp: Long, $entity: JSON!) {
      updateEntityV2(timestamp: $timestamp, entity: $entity) {
        entity
        __typename
      }
    }
"""

INVOKE_INTEGRATION_INSTANCE = """
    mutation InvokeIntegrationInstance(
        $id: String!
    ) {
        invokeIntegrationInstance(
            id: $id
        ) {
            success
            integrationJobId
        }
    }
"""

UPDATE_QUESTION = """
    mutation UpdateQuestion($id: ID!, $update: QuestionUpdate!) {
      updateQuestion(id: $id, update: $update) {
        ...QuestionFields
        __typename
      }
    }

    fragment QuestionFields on Question {
      id
      sourceId
      title
      name
      description
      tags
      lastUpdatedTimestamp
      queries {
        name
        query
        version
        resultsAre
        __typename
      }
      compliance {
        standard
        requirements
        controls
        __typename
      }
      variables {
        name
        required
        default
        __typename
      }
      tags
      accountId
      integrationDefinitionId
      showTrend
      pollingInterval
      __typename
    }
"""

DELETE_QUESTION = """
    mutation DeleteQuestion($id: ID!) {
      deleteQuestion(id: $id) {
        id
        title
        description
        queries {
          query
          name
          version
          __typename
        }
        compliance {
          standard
          requirements
          controls
          __typename
        }
        variables {
          name
          required
          default
          __typename
        }
        tags
        accountId
        integrationDefinitionId
        showTrend
        pollingInterval
        __typename
      }
    }
"""
