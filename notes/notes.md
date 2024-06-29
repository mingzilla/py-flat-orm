## Todo
* go through functions in in_fn
* make sure domain can be typed based on fields
  * use generate template function to set every single field, so that type is guaranteed
  * when setting values, use template for the type, allow setting values based on type, and None

For now, please give me these classes in python, I'll ask you the rest later

* ConnectionUtil
* OrmDomain
* 
* OrmMapping
* OrmMappingSpec
* 
* OrmFieldError
* OrmFieldErrors
* OrmConstraintType
* 
* OrmConstraint
* OrmConditionalValidate
* OrmErrorCollector
* 
* OrmValidate
* OrmValidateSpec
* 
* AbstractOrmDomain
* 
* OrmRead
* 
* OrmWrite
* OrmWriteSpec
* 
* MyPerson
* MyPersonSpec
* 
* RepoDb
* RepoDbSpec
* 
* OrmActor
* 
* MyApp






I would like to convert the groovy code below into python please, 
* I want to keep the same class names for each class, and the methods need to be in `underscore_case` for python
* please use SQLAlchemy
* InFn - assume this is already present
* IdGen, DomainUtil are already available as below

```python
import random


class IdGen:
    __LIMIT = 10000
    __MIN_VALUE = -99999999
    __MAX_VALUE = -98999999

    def __init__(self):
        self.__generated_numbers = set()
        self.__random = random.Random()

    @staticmethod
    def create():
        return IdGen()

    def get_int(self):
        if len(self.__generated_numbers) >= IdGen.__LIMIT:
            raise Exception("All unique numbers have been generated")

        new_number = None
        while new_number is None or new_number in self.__generated_numbers:
            new_number = self.__random.randint(IdGen.__MIN_VALUE, IdGen.__MAX_VALUE)

        self.__generated_numbers.add(new_number)
        return new_number

    def clear(self):
        self.__generated_numbers.clear()

    @staticmethod
    def is_generated_id(num):
        try:
            id = int(num)
        except ValueError:
            return False
        return IdGen.__MIN_VALUE <= id <= IdGen.__MAX_VALUE

```

```python
from typing import Any, Dict, TypeVar

from .in_fn import InFn

T = TypeVar('T')


class DomainUtil:

    @staticmethod
    def merge_fields(obj: T, new_props: Dict[str, Any]) -> T:
        new_props = new_props or {}
        relevant_props = {}

        for k, v in new_props.items():
            if hasattr(obj, k):
                relevant_props[k] = v

        for k, v in relevant_props.items():
            obj = InFn.set_primitive_field(obj, k, InFn.trim_to_empty_if_is_string(v))

        return obj

```

The below is for the groovy classes to be converted

```groovy
package uk.co.mingzilla.flatorm.util

import groovy.transform.CompileStatic

import java.sql.Connection
import java.sql.Driver

@CompileStatic
class ConnectionUtil {

    static Connection getConnection(String driverClassName, String url, Properties connectionProperties) {
        try {
            return ((Driver) Class.forName(driverClassName).newInstance()).connect(url, connectionProperties)
        } catch (Exception ex) {
            throw new RuntimeException(ex.message, ex)
        }
    }

    static void close(Connection connection) {
        try {
            connection?.close()
        } catch (Exception ignore) {
            // do nothing - don't mind if the close fails
        }
    }
}

```

```groovy
package uk.co.mingzilla.flatorm.domain.definition

import uk.co.mingzilla.flatorm.domain.validation.OrmErrorCollector

interface OrmDomain {

    List<OrmMapping> resolveMappings()

    OrmErrorCollector validate()

    Integer getId()

    void setId(Integer id)

    String tableName()
}
```

```groovy
package uk.co.mingzilla.flatorm.domain.definition

import groovy.transform.CompileStatic
import uk.co.mingzilla.flatorm.util.InFn

import java.sql.ResultSet

@CompileStatic
class OrmMapping {

    String camelFieldName
    String dbFieldName

    static OrmMapping create(String camelFieldName, String dbFieldName) {
        new OrmMapping(
                camelFieldName: camelFieldName,
                dbFieldName: dbFieldName.toLowerCase(),
        )
    }

    /**
     * Map the whole domain object, which allows custom mapping to override the default (dbField: snake case, domainField: camel case, id: maps to serial).
     * */
    static List<OrmMapping> mapDomain(Class aClass, List<OrmMapping> customMapping = null) {
        List<OrmMapping> defaults = createDomainDefault(aClass)
        List<OrmMapping> items = (customMapping && !customMapping.empty) ? (customMapping + defaults) : defaults
        return items.unique { it.camelFieldName }.sort { a, b -> a.dbFieldName <=> b.dbFieldName }
    }

    private static List<OrmMapping> createDomainDefault(Class aClass) {
        Object obj = aClass.newInstance() // create object regardless if it defines private constructor
        Map map = InFn.toMap(obj)
        List<String> fields = map.keySet() as List<String>

        fields.collect { String field ->
            String dbFieldName = InFn.camelToUpperSnakeCase(field)
            return create(field, dbFieldName)
        }
    }

    static <T> T toDomain(List<OrmMapping> dbDomainFieldMappings, ResultSet resultSet, Closure<T> createDomainFn) {
        Map props = dbDomainFieldMappings.collectEntries { OrmMapping mapping ->
            String key = mapping.camelFieldName
            String value = InFn.<String> safeGet(null, { resultSet.getObject(mapping.dbFieldName) })
            [(key): (value)]
        }

        return createDomainFn(props)
    }

    static List<List<OrmMapping>> splitIdAndNonIdMappings(List<OrmMapping> mappings) {
        OrmMapping idMapping = mappings.find { it.camelFieldName?.equalsIgnoreCase('id') }
        List<OrmMapping> nonIdMappings = mappings.findAll { it.camelFieldName != idMapping?.camelFieldName }
        return [[idMapping], nonIdMappings]
    }

    static OrmMapping getIdMapping(List<OrmMapping> mappings) {
        List<List<OrmMapping>> idAndNonIdMappings = splitIdAndNonIdMappings(mappings)
        return idAndNonIdMappings[0][0]
    }
}

```


```groovy
package uk.co.mingzilla.flatorm.domain.validation

import groovy.transform.CompileStatic

@CompileStatic
class OrmFieldError {

    OrmConstraint constraint // e.g., minValue 5
    String field // e.g., age
    Object invalidValue // e.g., 4

    static OrmFieldError create(OrmConstraint constraint, String field, Object invalidValue) {
        OrmFieldError item = new OrmFieldError()
        item.constraint = constraint
        item.field = field
        item.invalidValue = invalidValue
        return item
    }

    Map<String, Object> toMap() {
        Map<String, Object> m = [field: (field)] as Map<String, Object>
        m['constraint'] = constraint.type.value
        if (constraint.value != null) m['constraintValue'] = constraint.value
        if (constraint.values != null && !constraint.values.empty) m['constraintValues'] = constraint.values.join(', ')
        m['invalidValue'] = invalidValue
        return m
    }
}

```


```groovy
package uk.co.mingzilla.flatorm.domain.validation

import groovy.transform.CompileStatic

@CompileStatic
class OrmFieldErrors {

    String field // e.g., age
    List<OrmFieldError> errors = []

    static OrmFieldErrors create(String field) {
        return new OrmFieldErrors(field: field)
    }

    OrmFieldErrors addError(OrmFieldError fieldError) {
        errors.add(fieldError)
        return this
    }

    boolean hasErrors() {
        return !errors.empty
    }
}

```


```groovy
package uk.co.mingzilla.flatorm.domain.validation

enum OrmConstraintType {

    REQUIRED('REQUIRED'),
    MINIMUM_LENGTH('MINIMUM_LENGTH'),
    MINIMUM_VALUE('MINIMUM_VALUE'), // Have error calling it MIN_VALUE, so call it MINIMUM_VALUE
    MAXIMUM_VALUE('MAXIMUM_VALUE'),
    IN_LIST('IN_LIST'),
    NOT_IN_LIST('NOT_IN_LIST'),
    UNIQUE('UNIQUE')

    String value

    OrmConstraintType(String value) {
        this.value = value
    }
}
```


```groovy
package uk.co.mingzilla.flatorm.domain.validation

import groovy.transform.CompileStatic
import org.apache.commons.lang3.StringUtils
import uk.co.mingzilla.flatorm.util.InFn

@CompileStatic
class OrmConstraint {

    OrmConstraintType type // e.g., minValue
    String value // (optional) e.g., when minValue is 5, then 'type' is MINIMUM_VALUE, 'value' is set to 5
    List values // (optional) e.g., when inList is [1,2,3], then 'type' is IN_LIST, 'values' are [1,2,3]

    static OrmConstraint required() {
        return new OrmConstraint(type: OrmConstraintType.REQUIRED)
    }

    static OrmConstraint minLength(Integer value) {
        return new OrmConstraint(type: OrmConstraintType.MINIMUM_LENGTH, value: String.valueOf(value))
    }

    static OrmConstraint minValue(Integer value) {
        return new OrmConstraint(type: OrmConstraintType.MINIMUM_VALUE, value: String.valueOf(value))
    }

    static OrmConstraint maxValue(Integer value) {
        return new OrmConstraint(type: OrmConstraintType.MAXIMUM_VALUE, value: String.valueOf(value))
    }

    static OrmConstraint inList(List values) {
        return new OrmConstraint(type: OrmConstraintType.IN_LIST, values: values)
    }

    static OrmConstraint notInList(List values) {
        return new OrmConstraint(type: OrmConstraintType.NOT_IN_LIST, values: values)
    }

    static boolean isValid(OrmConstraint constraint, Object v) {
        switch (constraint.type) {
            case OrmConstraintType.REQUIRED:
                return StringUtils.isNotBlank(v as String)
            case OrmConstraintType.MINIMUM_LENGTH:
                return v == null || (String.valueOf(v ?: '').size() >= (constraint.value as Integer))
            case OrmConstraintType.MINIMUM_VALUE:
                return v == null || (InFn.isNumber(v) && InFn.asLong(v) >= (constraint.value as Integer))
            case OrmConstraintType.MAXIMUM_VALUE:
                return v == null || (InFn.isNumber(v) && InFn.asLong(v) <= (constraint.value as Integer))
            case OrmConstraintType.IN_LIST:
                return v == null || (v in constraint.values)
            case OrmConstraintType.NOT_IN_LIST:
                return v == null || (!(v in constraint.values))
            default:
                return true
        }
    }
}

```


```groovy
package uk.co.mingzilla.flatorm.domain.validation

import groovy.transform.CompileStatic
import uk.co.mingzilla.flatorm.domain.definition.OrmValidate

@CompileStatic
class OrmConditionalValidate {

    Closure<Boolean> conditionIsMetFn

    OrmErrorCollector then(OrmErrorCollector collector, String field, List<OrmConstraint> constraints) {
        if (!conditionIsMetFn(collector.domain)) return collector
        return OrmValidate.with(collector, field, constraints)
    }
}

```


```groovy
package uk.co.mingzilla.flatorm.domain.validation

import groovy.transform.CompileStatic
import uk.co.mingzilla.flatorm.domain.definition.OrmDomain

@CompileStatic
class OrmErrorCollector {

    OrmDomain domain
    Map<String, OrmFieldErrors> fields = [:] // key: name of a field, value: a collection of errors

    static OrmErrorCollector create(OrmDomain domain) {
        return new OrmErrorCollector(domain: domain)
    }

    void addError(OrmFieldError fieldError) {
        String field = fieldError.field
        if (!fields[(field)]) fields[(field)] = OrmFieldErrors.create(field)

        OrmFieldErrors fieldErrors = fields[(field)]
        fieldErrors.addError(fieldError)
    }

    boolean hasErrors() {
        return fields.find { it.value.hasErrors() } != null
    }

    static boolean haveErrors(List<List<OrmErrorCollector>> collectors) {
        OrmErrorCollector itemWithError = collectors.flatten().<OrmErrorCollector> toList().find { it?.hasErrors() }
        return itemWithError != null
    }

    static List<Map<String, List<Map>>> toErrorMaps(List<OrmErrorCollector> collectors) {
        List<OrmErrorCollector> itemWithError = collectors.<OrmErrorCollector> toList().findAll { it?.hasErrors() }
        return itemWithError*.toMap()
    }

    Map<String, List<Map>> toMap() {
        return fields.collectEntries {
            [(it.key): it.value.errors*.toMap()]
        }
    }
}

```

```groovy
package uk.co.mingzilla.flatorm.domain.definition

import groovy.transform.CompileStatic
import org.apache.commons.lang3.StringUtils
import uk.co.mingzilla.flatorm.domain.validation.OrmConditionalValidate
import uk.co.mingzilla.flatorm.domain.validation.OrmConstraint
import uk.co.mingzilla.flatorm.domain.validation.OrmErrorCollector
import uk.co.mingzilla.flatorm.domain.validation.OrmFieldError
import uk.co.mingzilla.flatorm.util.InFn

@CompileStatic
class OrmValidate {

    static OrmErrorCollector with(OrmErrorCollector collector, String field, List<OrmConstraint> constraints) {
        Object value = collector.domain[(field)]
        constraints.each {
            collectError(collector, it, field, value)
        }
        return collector
    }

    private static OrmErrorCollector collectError(OrmErrorCollector collector, OrmConstraint constraint, String field, Object value) {
        if (OrmConstraint.isValid(constraint, value)) return collector

        OrmFieldError fieldError = OrmFieldError.create(constraint, field, value)
        collector.addError(fieldError)
        return collector
    }

    static OrmConditionalValidate ifHaving(String field) {
        Closure<Boolean> conditionIsMetFn = { OrmDomain it ->
            String v = InFn.propAsString(field, it)
            return StringUtils.isNotBlank(v)
        }
        return new OrmConditionalValidate(conditionIsMetFn: conditionIsMetFn)
    }

    static OrmConditionalValidate ifNotHaving(String field) {
        Closure<Boolean> conditionIsMetFn = { OrmDomain it ->
            String v = InFn.propAsString(field, it)
            return StringUtils.isBlank(v)
        }
        return new OrmConditionalValidate(conditionIsMetFn: conditionIsMetFn)
    }

    static OrmConditionalValidate ifSatisfies(Closure<Boolean> conditionIsMetFn) {
        return new OrmConditionalValidate(conditionIsMetFn: conditionIsMetFn)
    }
}

```

```groovy
package uk.co.mingzilla.flatorm.domain.definition

import groovy.transform.CompileStatic
import uk.co.mingzilla.flatorm.domain.OrmRead
import uk.co.mingzilla.flatorm.domain.OrmWrite
import uk.co.mingzilla.flatorm.domain.validation.OrmErrorCollector

import java.sql.Connection

@CompileStatic
abstract class AbstractOrmDomain<T extends AbstractOrmDomain<T>> implements OrmDomain {

    @Override
    List<OrmMapping> resolveMappings() {
        return OrmMapping.mapDomain(this.class, [])
    }

    static <T extends AbstractOrmDomain<T>> Long count(Connection conn, Class<T> aClass) {
        return OrmRead.count(conn, aClass)
    }

    static <T extends AbstractOrmDomain<T>> List<T> listAll(Connection conn, Class<T> aClass) {
        return OrmRead.listAll(conn, aClass)
    }

    static <T extends AbstractOrmDomain<T>> T getById(Connection conn, Class<T> aClass, Integer id) {
        return OrmRead.getById(conn, aClass, id)
    }

    static <T extends AbstractOrmDomain<T>> T getFirst(Connection conn, Class<T> aClass, String selectStatement) {
        return OrmRead.getFirst(conn, aClass, selectStatement)
    }

    OrmErrorCollector validateAndSave(Connection conn) {
        return OrmWrite.validateAndSave(conn, this)
    }

    OrmDomain insertOrUpdate(Connection conn) {
        return OrmWrite.insertOrUpdate(conn, this)
    }

    boolean delete(Connection conn) {
        return OrmWrite.delete(conn, this)
    }
}

```


```groovy
package uk.co.mingzilla.flatorm.domain

import groovy.transform.CompileStatic
import uk.co.mingzilla.flatorm.domain.definition.OrmDomain
import uk.co.mingzilla.flatorm.domain.definition.OrmMapping
import uk.co.mingzilla.flatorm.util.DomainUtil
import uk.co.mingzilla.flatorm.util.InFn

import java.sql.Connection
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.sql.SQLException

@CompileStatic
class OrmRead {

    static Closure<PreparedStatement> NO_PARAMS = { PreparedStatement it -> it }

    /**
     * List objects with a given select statement. Connection is not closed.
     * Always wraps the whole request and response with try/catch/finally close.
     */
    static <T> List<T> listAll(Connection conn, Class aClass) {
        OrmDomain domain = aClass.newInstance() as OrmDomain
        List<OrmMapping> mappings = domain.resolveMappings()

        String selectStatement = "select * from ${domain.tableName()}"
        return listAndMerge(conn, mappings, selectStatement, NO_PARAMS,
                { Map props ->
                    Object obj = aClass.newInstance()
                    DomainUtil.mergeFields(obj, props) as T
                })
    }

    /**
     * Similar to {@link #listAll}. Intended to be used with a custom WHERE clause.
     */
    static <T> List<T> list(Connection conn, Class aClass, String selectStatement, Closure<PreparedStatement> setParamsFn) {
        List<OrmMapping> mappings = (aClass.newInstance() as OrmDomain).resolveMappings()

        return listAndMerge(conn, mappings, selectStatement, setParamsFn,
                { Map props ->
                    Object obj = aClass.newInstance()
                    DomainUtil.mergeFields(obj, props) as T
                })
    }

    /**
     * List objects with a given select statement. Connection is not closed.
     * Always wraps the whole request and response with try/catch/finally close.
     */
    static <T> List<T> listAndMerge(Connection conn, List<OrmMapping> dbDomainFieldMappings, String selectStatement, Closure<PreparedStatement> setParamsFn, Closure<T> createDomainFn) {
        List<T> objs = []
        PreparedStatement statement
        ResultSet resultSet

        try {
            statement = conn.prepareStatement(selectStatement.toString())
            statement = setParamsFn(statement)
            resultSet = statement.executeQuery()

            while (resultSet.next()) {
                T domain = OrmMapping.toDomain(dbDomainFieldMappings, resultSet, createDomainFn)
                objs.add(domain)
            }
        } catch (SQLException sqlEx) {
            RuntimeException ex = new RuntimeException("Failed running select statement to create object: $sqlEx.message", sqlEx)
            throw ex
        }
        return objs
    }

    /**
     * When used, the select statement typically needs a WHERE clause.
     */
    static <T> T getById(Connection conn, Class aClass, def id) {
        OrmDomain domain = aClass.newInstance() as OrmDomain
        List<OrmMapping> mappings = domain.resolveMappings()

        String idField = mappings.find { it.camelFieldName == 'id' }?.dbFieldName
        String selectStatement = "SELECT * FROM ${domain.tableName()} WHERE ${idField} = ${id}"
        return getAndMerge(conn, mappings, selectStatement,
                { Map props ->
                    Object obj = aClass.newInstance()
                    DomainUtil.mergeFields(obj, props) as T
                })
    }

    /**
     * When used, the select statement typically needs a WHERE clause.
     */
    static <T> T getFirst(Connection conn, Class aClass, String selectStatement) {
        List<OrmMapping> mappings = (aClass.newInstance() as OrmDomain).resolveMappings()

        return getAndMerge(conn, mappings, selectStatement,
                { Map props ->
                    Object obj = aClass.newInstance()
                    DomainUtil.mergeFields(obj, props) as T
                })
    }

    /**
     * Same as {@link #listAndMerge}, but only return the 1st object found
     */
    static <T> T getAndMerge(Connection conn, List<OrmMapping> dbDomainFieldMappings, String selectStatement, Closure<T> createDomainFn) {
        try {
            PreparedStatement statement = conn.prepareStatement(selectStatement.toString())
            ResultSet resultSet = statement.executeQuery()
            try {
                resultSet.next()
                return OrmMapping.toDomain(dbDomainFieldMappings, resultSet, createDomainFn)
            } catch (Exception ignore) {
                return null // if valid SQL doesn't have data, then return null
            }
        } catch (SQLException sqlEx) {
            RuntimeException ex = new RuntimeException("Failed running select statement to create object: $sqlEx.message", sqlEx)
            throw ex
        }
    }

    /**
     * Count table records with a given table name.
     */
    static Long count(Connection conn, Class aClass) {
        OrmDomain domain = aClass.newInstance() as OrmDomain
        String selectStatement = "select count(*) from ${domain.tableName()}".toString()
        return getCount(conn, selectStatement)
    }

    /**
     * Intended to be used for a SELECT count(*) statement, which also allows e.g. JOIN and WHERE clause.
     */
    private static Long getCount(Connection conn, String selectStatement) {
        PreparedStatement statement
        ResultSet resultSet

        Long count = 0
        try {
            statement = conn.prepareStatement(selectStatement)
            resultSet = statement.executeQuery()

            while (resultSet.next()) {
                count = InFn.asLong(resultSet.getObject(1))
            }
        } catch (SQLException e) {
            throw new RuntimeException("Failed running select statement to count records: " + e.message, e)
        }

        return count
    }
}

```


```groovy
package uk.co.mingzilla.flatorm.domain

import groovy.transform.CompileStatic
import uk.co.mingzilla.flatorm.domain.definition.OrmDomain
import uk.co.mingzilla.flatorm.domain.definition.OrmMapping
import uk.co.mingzilla.flatorm.domain.validation.OrmErrorCollector
import uk.co.mingzilla.flatorm.util.IdGen
import uk.co.mingzilla.flatorm.util.InFn

import java.sql.*
import java.util.Date

@CompileStatic
class OrmWrite {

    static OrmErrorCollector validateAndSave(Connection conn, OrmDomain domain) {
        OrmErrorCollector errorCollector = domain.validate()
        if (!errorCollector.hasErrors()) {
            insertOrUpdate(conn, domain)
        }
        return errorCollector
    }

    static boolean delete(Connection conn, OrmDomain domain) {
        PreparedStatement statement = createDeletePreparedStatement(conn, domain)
        int rowsAffected = statement.executeUpdate()
        return rowsAffected > 0 // return true if row is deleted
    }

    static OrmDomain insertOrUpdate(Connection conn, OrmDomain domain) {
        boolean isNew = IdGen.isGeneratedId(domain.id)
        if (isNew) {
            PreparedStatement statement = createInsertPreparedStatement(conn, domain)
            int rowsAffected = statement.executeUpdate()
            if (rowsAffected > 0) {
                OrmMapping idMapping = OrmMapping.getIdMapping(domain.resolveMappings())
                domain.id = resolveId(statement.generatedKeys, idMapping)
            }
        } else {
            PreparedStatement updateStmt = createUpdatePreparedStatement(conn, domain)
            updateStmt.executeUpdate()
        }
        return domain
    }

    private static PreparedStatement createInsertPreparedStatement(Connection conn, OrmDomain domain) {
        List<List<OrmMapping>> idAndNonIdMappings = OrmMapping.splitIdAndNonIdMappings(domain.resolveMappings())
        List<OrmMapping> nonIdMappings = idAndNonIdMappings[1]
        String sql = createInsertStatement(domain.tableName(), nonIdMappings)
        PreparedStatement statement = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)
        statement = setStatementParams(statement, domain, nonIdMappings)
        return statement
    }

    private static String createInsertStatement(String tableName, List<OrmMapping> nonIdMappings) {
        String fieldNames = nonIdMappings*.dbFieldName.join(', ')
        String valuePlaceholders = nonIdMappings.collect { '?' }.join(', ')
        return """insert into ${tableName.toLowerCase()} (${fieldNames}) values (${valuePlaceholders})"""
    }

    private static PreparedStatement createUpdatePreparedStatement(Connection conn, OrmDomain domain) {
        List<List<OrmMapping>> idAndNonIdMappings = OrmMapping.splitIdAndNonIdMappings(domain.resolveMappings())
        OrmMapping idMapping = idAndNonIdMappings[0][0]
        List<OrmMapping> nonIdMappings = idAndNonIdMappings[1]
        String sql = createUpdateStatement(domain.tableName(), domain.id, idMapping, nonIdMappings)
        PreparedStatement statement = conn.prepareStatement(sql)
        statement = setStatementParams(statement, domain, nonIdMappings)
        return statement
    }

    private static String createUpdateStatement(String tableName, Integer id, OrmMapping idMapping, List<OrmMapping> nonIdMappings) {
        if (!idMapping) throw new UnsupportedOperationException('Missing OrmMapping for id')
        String setStatement = nonIdMappings.collect { "${it.dbFieldName} = ?" }.join(', ')
        return """update ${tableName.toLowerCase()} set ${setStatement} where ${idMapping.dbFieldName} = ${String.valueOf(id)}"""
    }

    private static PreparedStatement createDeletePreparedStatement(Connection conn, OrmDomain domain) {
        List<List<OrmMapping>> idAndNonIdMappings = OrmMapping.splitIdAndNonIdMappings(domain.resolveMappings())
        OrmMapping idMapping = idAndNonIdMappings[0][0]
        String sql = createDeleteStatement(domain.tableName(), idMapping)
        PreparedStatement statement = conn.prepareStatement(sql)
        statement.setInt(1, domain.id);
        return statement
    }

    private static String createDeleteStatement(String tableName, OrmMapping idMapping) {
        if (!idMapping) throw new UnsupportedOperationException('Missing OrmMapping for id')
        return """delete from ${tableName.toLowerCase()} where ${idMapping.dbFieldName} = ?"""
    }

    private static PreparedStatement setStatementParams(PreparedStatement statement, OrmDomain domain, List<OrmMapping> nonIdMappings) {
        nonIdMappings.eachWithIndex { OrmMapping it, Integer index ->
            Integer oneBasedPosition = index + 1
            Class type = InFn.getType(domain.class, it.camelFieldName)
            switch (type) {
                case boolean:
                case Boolean.class:
                    Boolean v = InFn.propAsBoolean(it.camelFieldName, domain)
                    statement.setBoolean(oneBasedPosition, v)
                    break
                case BigDecimal.class:
                    BigDecimal v = InFn.propAsBigDecimal(it.camelFieldName, domain)
                    statement.setBigDecimal(oneBasedPosition, v)
                    break
                case Date.class:
                    try {
                        Date d = InFn.prop(it.camelFieldName, domain) as Date
                        statement.setDate(oneBasedPosition, new java.sql.Date(d.time))
                    } catch (Exception ignore) {
                        // ignore invalid date
                    }
                    break
                case double:
                case Double.class:
                    Double v = InFn.propAsDouble(it.camelFieldName, domain)
                    statement.setDouble(oneBasedPosition, v)
                    break
                case float:
                case Float.class:
                    Float v = InFn.propAsFloat(it.camelFieldName, domain)
                    statement.setFloat(oneBasedPosition, v)
                    break
                case int:
                case Integer.class:
                    Integer v = InFn.propAsInteger(it.camelFieldName, domain)
                    statement.setInt(oneBasedPosition, v)
                    break
                case long:
                case Long.class:
                    Long v = InFn.propAsLong(it.camelFieldName, domain)
                    statement.setLong(oneBasedPosition, v)
                    break
                case String.class:
                    String v = InFn.propAsString(it.camelFieldName, domain)
                    statement.setString(oneBasedPosition, v)
                    break
                default:
                    break
            }
        }

        return statement
    }

    private static Integer resolveId(ResultSet generatedKeys, OrmMapping idMapping) {
        if (!idMapping) throw new UnsupportedOperationException('Missing OrmMapping for id')
        if (!generatedKeys.next()) return null // call next() to move the ResultSet cursor
        ResultSetMetaData metaData = generatedKeys.metaData
        int columnCount = metaData.columnCount
        for (int i = 1; i <= columnCount; i++) {
            String columnName = metaData.getColumnName(i)
            if (idMapping.dbFieldName.equalsIgnoreCase(columnName)) {
                return generatedKeys.getInt(i)
            }
        }
        // it is possible that a driver is implemented to return 'insert_id' (rather than using the actual column name) as the columnName
        // If that happens, we fallback to use 1. Typically, the generated key is the first column in the ResultSet
        return generatedKeys.getInt(1)
    }
}

```


```groovy
package uk.co.mingzilla.flatorm.domain

import groovy.transform.CompileStatic
import uk.co.mingzilla.flatorm.util.ConnectionUtil

import java.sql.Connection

@CompileStatic
class OrmActor {

    static <T> T run(Connection connection, Closure<T> fn) {
        if (!connection) return null
        T result = null
        try {
            result = fn(connection)
        } catch (Exception ignore) {
        } finally {
            ConnectionUtil.close(connection)
        }
        return result
    }

    /**
     * Run in a transaction.
     */
    static <T> T runInTx(Connection connection, Closure<T> fn) {
        if (!connection) return null
        T result = null
        try {
            connection.setAutoCommit(false)
            result = fn(connection)
            connection.commit()
        } catch (Exception ignore) {
            connection.rollback()
        } finally {
            ConnectionUtil.close(connection)
        }
        return result
    }

    static void terminate() {
        throw new Exception('Terminate transaction and rollback')
    }
}

```


```groovy
package uk.co.mingzilla.example

import groovy.transform.CompileStatic
import uk.co.mingzilla.flatorm.domain.OrmRead
import uk.co.mingzilla.flatorm.domain.definition.AbstractOrmDomain
import uk.co.mingzilla.flatorm.domain.definition.OrmDomain
import uk.co.mingzilla.flatorm.domain.definition.OrmMapping
import uk.co.mingzilla.flatorm.domain.definition.OrmValidate
import uk.co.mingzilla.flatorm.domain.validation.OrmErrorCollector

import java.sql.Connection
import java.sql.PreparedStatement

import static uk.co.mingzilla.flatorm.domain.validation.OrmConstraint.minLength
import static uk.co.mingzilla.flatorm.domain.validation.OrmConstraint.required

@CompileStatic
class MyPerson implements OrmDomain {

    Integer id
    String name

    @Override
    List<OrmMapping> resolveMappings() {
        return OrmMapping.mapDomain(MyPerson.class, [
                OrmMapping.create('id', 'serial'),
                OrmMapping.create('name', 'usercode'),
        ])
    }

    @Override
    OrmErrorCollector validate() {
        OrmErrorCollector item = OrmErrorCollector.create(this)
        OrmValidate.with(item, 'id', [required()])
        OrmValidate.with(item, 'name', [required()])
        OrmValidate.ifSatisfies({ id == 1 }).then(item, 'name', [minLength(5)])
        return item
    }

    @Override
    String tableName() {
        return 'mis_users'
    }

    static List<MyPerson> listByNameStartsWith(Connection connection, String prefix) {
        String sql = """
        select * 
        from mis_users
        where usercode like ?
        """
        return OrmRead.list(connection, MyPerson.class, sql, { PreparedStatement it ->
            it.setString(1, "${prefix}%")
            return it
        })
    }
}

```


```groovy
package uk.co.mingzilla.example

import groovy.transform.CompileStatic
import uk.co.mingzilla.flatorm.domain.conn.ConnectionDetail
import uk.co.mingzilla.flatorm.util.ConnectionUtil

import java.sql.Connection

@CompileStatic
class RepoDb {

    static Connection getConn() {
        try {
            return createTargetDbConnection()
        } catch (Exception ex) {
            // Log error here. OrmActor expects a connection.
            throw new RuntimeException(ex.message, ex)
        }
    }

    private static Connection createTargetDbConnection() {
        ConnectionDetail detail = ConnectionDetail.create([
                "driverClassName": "org.mariadb.jdbc.Driver",
                "url"            : "jdbc:mariadb://localhost:3316/storage",
                "user"           : "root",
                "password"       : "test1234",
        ])
        return ConnectionUtil.getConnection(detail.driverClassName, detail.url, detail.connProperties)
    }
}

```


```groovy
package uk.co.mingzilla.example

import groovy.transform.CompileStatic
import uk.co.mingzilla.flatorm.domain.OrmActor
import uk.co.mingzilla.flatorm.domain.OrmRead
import uk.co.mingzilla.flatorm.domain.OrmWrite
import uk.co.mingzilla.flatorm.domain.validation.OrmErrorCollector
import uk.co.mingzilla.flatorm.util.IdGen

import java.sql.Connection

@CompileStatic
class MyApp {

    static void main(String[] args) {
        runWithoutTx()
        runWithTx()
    }

    static void runWithoutTx() {
        OrmActor.run(RepoDb.conn, { Connection conn ->
            println 'run'
            IdGen idGen = IdGen.create() // <-
            List<MyPerson> people1 = OrmRead.listAll(conn, MyPerson.class) // <- Example usage
            List<MyPerson> people2 = MyPerson.listByNameStartsWith(conn, 'An') // <-
            MyPerson person = OrmRead.getById(conn, MyPerson.class, 1) // <-

            println OrmRead.count(conn, MyPerson.class) // <-
            println people1*.name.join(', ')
            println people2*.name.join(', ')
            println person?.name

            MyPerson p = new MyPerson(id: idGen.int, name: 'Andrew')
            OrmErrorCollector collector = OrmWrite.validateAndSave(conn, p) // <-

            println p.id
            println collector.hasErrors() // <-
            println OrmRead.count(conn, MyPerson.class)

            boolean isDeleted = OrmWrite.delete(conn, p) // <-
            println isDeleted
            println OrmRead.count(conn, MyPerson.class)
        })
    }

    static void runWithTx() {
        Map errorMap = [:]
        OrmActor.runInTx(RepoDb.conn, { Connection conn ->
            println 'runInTx'
            IdGen idGen = IdGen.create() // <-

            println OrmRead.count(conn, MyPerson.class)
            OrmErrorCollector collector1 = OrmWrite.validateAndSave(conn, new MyPerson(id: idGen.int, name: 'Bobby')) // <- success
            println OrmRead.count(conn, MyPerson.class)

            MyPerson p = new MyPerson(name: 'Christine')
            OrmErrorCollector collector2 = OrmWrite.validateAndSave(conn, p) // <- failure
            println OrmRead.count(conn, MyPerson.class)

            List<OrmErrorCollector> people = [collector1, collector2]
            boolean haveErrors = OrmErrorCollector.haveErrors([people])
            if (haveErrors) {
                errorMap = [people: OrmErrorCollector.toErrorMaps(people)]
                OrmActor.terminate() // <- trigger rollback, so that Bobby is not saved
            }
        })

        // when used in a controller, this can be returned as an API response
        println errorMap // [people:[[id:[[field:id, constraint:REQUIRED, invalidValue:null]]]]]
    }
}

```

And the below are unit tests to help you to create the desired python outcome

```groovy
package uk.co.mingzilla.example

import spock.lang.Specification
import uk.co.mingzilla.flatorm.domain.validation.OrmErrorCollector

class MyPersonSpec extends Specification {

    def "Test creation"() {
        expect:
        new MyPerson() != null
    }

    void "Test validate"() {
        given:
        MyPerson person = new MyPerson(id: 1, name: 'Andy')

        when:
        OrmErrorCollector domainErrors = person.validate()

        then:
        assert domainErrors.hasErrors()
        assert domainErrors.toMap() == [
                'name': [
                        [constraint: 'MINIMUM_LENGTH', constraintValue: '5', field: 'name', invalidValue: 'Andy']
                ]
        ]
    }
}

```


```groovy
package uk.co.mingzilla.example

import spock.lang.Specification
import uk.co.mingzilla.flatorm.domain.OrmActor
import uk.co.mingzilla.flatorm.domain.OrmRead

import java.sql.Connection

class RepoDbSpec extends Specification {

    void "Test run"() {
        given:
        List<MyPerson> people1 = []
        List<MyPerson> people2 = []
        MyPerson person
        long count = 0

        OrmActor.run(RepoDb.conn, { Connection connection ->
            people1 = OrmRead.listAll(connection, MyPerson.class)
            people2 = MyPerson.listByNameStartsWith(connection, 'A') // custom sql
            person = OrmRead.getById(connection, MyPerson.class, 1)
            count = OrmRead.count(connection, MyPerson.class)
        })

        expect:
        people1.size() > 0
        people2.size() > 0
        person != null
        count > 0
    }

    void "Test runInTx"() {
        given:
        List<MyPerson> people1 = []
        List<MyPerson> people2 = []
        MyPerson person

        OrmActor.runInTx(RepoDb.conn, { Connection connection ->
            people1 = OrmRead.listAll(connection, MyPerson.class)
            people2 = MyPerson.listByNameStartsWith(connection, 'A') // custom sql
            person = OrmRead.getById(connection, MyPerson.class, 1)
        })

        expect:
        people1.size() > 0
        people2.size() > 0
        person != null
    }
}

```


```groovy
package uk.co.mingzilla.flatorm.domain.definition

import spock.lang.Specification
import spock.lang.Unroll
import uk.co.mingzilla.example.MyPerson

import java.sql.ResultSet

class OrmMappingSpec extends Specification {

    def "Test mapDomain"() {
        when:
        List<OrmMapping> items = OrmMapping.mapDomain(MyPerson.class, [
                OrmMapping.create('id', 'SERIAL'),
        ])

        then:
        items.camelFieldName.containsAll(['id', 'name'])
        items.dbFieldName.containsAll(['SERIAL', 'NAME'])
    }

    @Unroll
    def "test create method with camelFieldName: #camelFieldName and dbFieldName: #dbFieldName"() {
        when:
        OrmMapping ormMapping = OrmMapping.create(camelFieldName, dbFieldName)

        then:
        ormMapping.camelFieldName == camelFieldName
        ormMapping.dbFieldName == dbFieldName

        where:
        camelFieldName | dbFieldName
        "name"         | "NAME"
        "age"          | "AGE"
        "address"      | "ADDRESS"
    }

    def "test mapDomain with default mappings"() {
        given:
        List<OrmMapping> expectedMappings = [
                OrmMapping.create("name", "NAME"),
                OrmMapping.create("age", "AGE"),
                OrmMapping.create("active", "ACTIVE")
        ]

        when:
        List<OrmMapping> mappings = OrmMapping.mapDomain(TestDomain.class)

        then:
        mappings.size() == expectedMappings.size()
        mappings*.camelFieldName.containsAll(expectedMappings*.camelFieldName)
        mappings*.dbFieldName.containsAll(expectedMappings*.dbFieldName)
    }

    def "test mapDomain with custom mappings"() {
        given:
        List<OrmMapping> customMappings = [OrmMapping.create("customField", "CUSTOM_FIELD")]
        List<OrmMapping> expectedMappings = customMappings + [
                OrmMapping.create("name", "NAME"),
                OrmMapping.create("age", "AGE"),
                OrmMapping.create("active", "ACTIVE")
        ]

        when:
        List<OrmMapping> mappings = OrmMapping.mapDomain(TestDomain.class, customMappings)

        then:
        mappings.size() == expectedMappings.size()
        mappings*.camelFieldName.containsAll(expectedMappings*.camelFieldName)
        mappings*.dbFieldName.containsAll(expectedMappings*.dbFieldName)
    }

    def "test toDomain method"() {
        given:
        ResultSet resultSet = Mock(ResultSet)
        resultSet.getObject("NAME") >> "John"
        resultSet.getObject("AGE") >> 25
        resultSet.getObject("ACTIVE") >> true

        List<OrmMapping> mappings = [
                OrmMapping.create("name", "NAME"),
                OrmMapping.create("age", "AGE"),
                OrmMapping.create("active", "ACTIVE")
        ]

        when:
        TestDomain domain = OrmMapping.toDomain(mappings, resultSet, { props -> new TestDomain(props) })

        then:
        domain.name == "John"
        domain.age == 25
        domain.active
    }

    static class TestDomain {
        String name
        Integer age
        Boolean active

        TestDomain(Map<String, Object> props) {
            if (props) {
                this.name = props['name']
                this.age = props['age'] as int
                this.active = props['active'] as boolean
            }
        }
    }
}

```


```groovy
package uk.co.mingzilla.flatorm.domain.definition

import groovy.transform.CompileStatic
import spock.lang.Specification
import spock.lang.Unroll
import uk.co.mingzilla.flatorm.domain.validation.OrmErrorCollector

import static uk.co.mingzilla.flatorm.domain.validation.OrmConstraint.*

class OrmValidateSpec extends Specification {

    @Unroll
    void "Test required"() {
        given:
        OrmErrorCollector item = OrmErrorCollector.create(new Person([(field): (value)]))

        when:
        OrmValidate.with(item, 'name', [required()])

        then:
        assert item.hasErrors() != isValid

        where:
        field  | value  | isValid
        'name' | ' '    | false
        'name' | 'Andy' | true
    }

    @Unroll
    void "Test minLength"() {
        given:
        OrmErrorCollector item = OrmErrorCollector.create(new Person([(field): (value)]))

        when:
        OrmValidate.with(item, 'name', [minLength(3)])

        then:
        assert item.hasErrors() != isValid

        where:
        field  | value  | isValid
        'name' | 'Andy' | true
        'name' | 'Yo'   | false
        'name' | null   | true // if field is required, use required for validation
    }

    @Unroll
    void "Test minValue, maxValue"() {
        given:
        OrmErrorCollector item = OrmErrorCollector.create(new Person([(field): (value)]))

        when:
        OrmValidate.with(item, 'age', [minValue(18), maxValue(80)])

        then:
        assert item.hasErrors() != isValid

        where:
        field | value | isValid
        'age' | 18    | true // minValue
        'age' | 17    | false
        'age' | null  | true

        'age' | 80    | true // maxValue
        'age' | 81    | false
    }

    @Unroll
    void "Test inList - text"() {
        given:
        OrmErrorCollector item = OrmErrorCollector.create(new Person([(field): (value)]))

        when:
        OrmValidate.with(item, 'gender', [inList(['male', 'female'])])

        then:
        assert item.hasErrors() != isValid

        where:
        field    | value  | isValid
        'gender' | 'male' | true
        'gender' | 'M'    | false
        'gender' | null   | true
    }

    @Unroll
    void "Test inList - number"() {
        given:
        OrmErrorCollector item = OrmErrorCollector.create(new Person([(field): (value)]))

        when:
        OrmValidate.with(item, 'bornMonth', [inList(1..12)])

        then:
        assert item.hasErrors() != isValid

        where:
        field       | value | isValid
        'bornMonth' | 1     | true
        'bornMonth' | 12    | true
        'bornMonth' | 0     | false
        'bornMonth' | 13    | false
        'bornMonth' | null  | true
    }

    @Unroll
    void "Test notInList - text"() {
        given:
        OrmErrorCollector item = OrmErrorCollector.create(new Person([(field): (value)]))

        when:
        OrmValidate.with(item, 'gender', [notInList(['male', 'female'])])

        then:
        assert item.hasErrors() != isValid

        where:
        field    | value  | isValid
        'gender' | 'male' | false
        'gender' | 'M'    | true
        'gender' | null   | true
    }

    @Unroll
    void "Test notInList - number"() {
        given:
        OrmErrorCollector item = OrmErrorCollector.create(new Person([(field): (value)]))

        when:
        OrmValidate.with(item, 'bornMonth', [notInList(1..12)])

        then:
        assert item.hasErrors() != isValid

        where:
        field       | value | isValid
        'bornMonth' | 1     | false
        'bornMonth' | 12    | false
        'bornMonth' | 0     | true
        'bornMonth' | 13    | true
        'bornMonth' | null  | true
    }

    @Unroll
    void "Test ifHaving"() {
        given:
        Person person = new Person()
        person.name = name
        person.age = age
        OrmErrorCollector item = OrmErrorCollector.create(person)

        when:
        OrmValidate.ifHaving('name').then(item, 'age', [required()])

        then:
        assert item.hasErrors() != isValid

        where:
        name   | age  | isValid
        'Andy' | 20   | true
        'Andy' | null | false
        null   | null | true
        null   | 20   | true
    }

    @Unroll
    void "Test ifNotHaving"() {
        given:
        Person person = new Person()
        person.name = name
        person.age = age
        OrmErrorCollector item = OrmErrorCollector.create(person)

        when:
        OrmValidate.ifNotHaving('name').then(item, 'age', [required()])

        then:
        assert item.hasErrors() != isValid

        where:
        name   | age  | isValid
        'Andy' | 20   | true
        'Andy' | null | true
        null   | null | false
        null   | 20   | true
    }

    @Unroll
    void "Test ifSatisfies - required"() {
        given:
        Person person = new Person()
        person.name = name
        person.age = age
        OrmErrorCollector item = OrmErrorCollector.create(person)

        when:
        OrmValidate.ifSatisfies({ age > 35 }).then(item, 'name', [required()])

        then:
        assert item.hasErrors() != isValid

        where:
        age  | name   | isValid
        40   | 'Andy' | true
        40   | null   | false

        20   | 'Andy' | true
        20   | null   | true
        null | 'Andy' | true
        null | null   | true
    }

    @Unroll
    void "Test ifSatisfies - minLength"() {
        given:
        Person person = new Person()
        person.name = name
        person.age = age
        OrmErrorCollector item = OrmErrorCollector.create(person)

        when:
        OrmValidate.ifSatisfies({ age > 35 }).then(item, 'name', [minLength(3)])

        then:
        assert item.hasErrors() != isValid

        where:
        age  | name   | isValid
        40   | 'Andy' | true
        40   | 'Yo'   | false
        40   | null   | true

        20   | 'Andy' | true
        20   | null   | true
        null | 'Andy' | true
        null | null   | true
    }

    @Unroll
    void "Test ifSatisfies - minValue, maxValue"() {
        given:
        Person person = new Person()
        person.name = name
        person.age = age
        OrmErrorCollector item = OrmErrorCollector.create(person)

        when:
        OrmValidate.ifSatisfies({ name == 'Andy' }).then(item, 'age', [minValue(18), maxValue(80)])

        then:
        assert item.hasErrors() != isValid

        where:
        name   | age  | isValid
        'Andy' | 18   | true
        'Andy' | 17   | false
        'Andy' | null | true
        'Andy' | 80   | true
        'Andy' | 81   | false

        'Bob'  | 18   | true
        'Bob'  | 17   | true
        'Bob'  | null | true
        'Bob'  | 80   | true
        'Bob'  | 81   | true
    }

    @Unroll
    void "Test ifSatisfies - inList"() {
        given:
        Person person = new Person()
        person.name = name
        person.gender = gender
        OrmErrorCollector item = OrmErrorCollector.create(person)

        when:
        OrmValidate.ifSatisfies({ name == 'Andy' }).then(item, 'gender', [inList(['male', 'female'])])

        then:
        assert item.hasErrors() != isValid

        where:
        name   | gender | isValid
        'Andy' | 'male' | true
        'Andy' | 'M'    | false
        'Andy' | null   | true

        'Bob'  | 'male' | true
        'Bob'  | 'M'    | true
        'Bob'  | null   | true
    }

    @Unroll
    void "Test ifSatisfies - notInList"() {
        given:
        Person person = new Person()
        person.name = name
        person.gender = gender
        OrmErrorCollector item = OrmErrorCollector.create(person)

        when:
        OrmValidate.ifSatisfies({ name == 'Andy' }).then(item, 'gender', [notInList(['male', 'female'])])

        then:
        assert item.hasErrors() != isValid

        where:
        name   | gender | isValid
        'Andy' | 'male' | false
        'Andy' | 'M'    | true
        'Andy' | null   | true

        'Bob'  | 'male' | true
        'Bob'  | 'M'    | true
        'Bob'  | null   | true
    }

    @CompileStatic
    private static class Person implements OrmDomain {

        Integer id
        String name
        Integer age
        String gender
        Integer bornMonth

        @Override
        List<OrmMapping> resolveMappings() {
            return OrmMapping.mapDomain(Person.class, [])
        }

        @Override
        OrmErrorCollector validate() {
            // Example implementation of a validate function
            OrmErrorCollector item = OrmErrorCollector.create(this)

            OrmValidate.with(item, 'name', [required(), minLength(3)])
            OrmValidate.with(item, 'age', [minValue(18), maxValue(80), notInList(60..64)])
            OrmValidate.with(item, 'gender', [inList(['male', 'female'])])
            OrmValidate.ifHaving('name').then(item, 'age', [required()])

            return item
        }

        @Override
        String tableName() {
            return 'PERSON'
        }
    }
}

```


based on your understanding of the code base, and the selected python class OrmValidate, convert unit tests `OrmValidateSpec` into python `unittest` tests
* just give me the code, you don't need to explain

```groovy
package uk.co.mingzilla.flatorm.domain

import spock.lang.Specification
import uk.co.mingzilla.flatorm.domain.definition.OrmDomain
import uk.co.mingzilla.flatorm.domain.definition.OrmMapping
import uk.co.mingzilla.flatorm.domain.validation.OrmErrorCollector

import java.sql.PreparedStatement

class OrmWriteSpec extends Specification {

    private class MyPerson implements OrmDomain {
        boolean booleanField
        Boolean boolean2Field

        BigDecimal bigDecimalField

        Date dateField

        double doubleField
        Double double2Field

        float floatField
        Float float2Field

        int idField
        Integer id

        long longField
        Long long2Field

        String name

        @Override
        List<OrmMapping> resolveMappings() {
            return OrmMapping.mapDomain(MyPerson.class, [])
        }

        @Override
        OrmErrorCollector validate() {
            return null
        }

        @Override
        String tableName() {
            return 'people'
        }
    }

    def "Test setStatementParams method"() {
        given:
        OrmDomain person = new MyPerson(
                id: 1,
                booleanField: true,
                boolean2Field: false,
                bigDecimalField: 100,
                dateField: new Date(),
                doubleField: 2.20,
                double2Field: 4.20,
                floatField: 1.20,
                float2Field: 3.20,
                idField: 5,
                longField: 11L,
                long2Field: 12L,
                name: 'John',
        )
        List<List<OrmMapping>> idAndNonIdMappings = OrmMapping.splitIdAndNonIdMappings(person.resolveMappings())
        List<OrmMapping> nonIdMappings = idAndNonIdMappings[1]

        // Mock PreparedStatement
        PreparedStatement statement = Mock(PreparedStatement)

        when:
        OrmWrite.setStatementParams(statement, person, nonIdMappings)

        then:
        1 * statement.setBigDecimal(1, person.bigDecimalField)
        1 * statement.setBoolean(2, person.boolean2Field)
        1 * statement.setBoolean(3, person.booleanField)
        1 * statement.setDate(4, person.dateField)
        1 * statement.setDouble(5, person.double2Field)
        1 * statement.setDouble(6, person.doubleField)
        1 * statement.setFloat(7, person.float2Field)
        1 * statement.setFloat(8, person.floatField)
        1 * statement.setInt(9, person.idField)
        1 * statement.setLong(10, person.long2Field)
        1 * statement.setLong(11, person.longField)
        1 * statement.setString(12, person.name)
    }

    def "Test createInsertStatement method"() {
        given:
        String tableName = "MY_TABLE"
        List<OrmMapping> nonIdMappings = [
                new OrmMapping(camelFieldName: "name", dbFieldName: "Name"),
                new OrmMapping(camelFieldName: "age", dbFieldName: "Age")
        ]

        when:
        String insertStatement = OrmWrite.createInsertStatement(tableName, nonIdMappings)

        then:
        insertStatement == "insert into my_table (Name, Age) values (?, ?)"
    }

    def "Test createUpdateStatement method"() {
        given:
        String tableName = "MY_TABLE"
        Integer id = 1
        OrmMapping idMapping = new OrmMapping(camelFieldName: "id", dbFieldName: "ID")
        List<OrmMapping> nonIdMappings = [
                new OrmMapping(camelFieldName: "name", dbFieldName: "Name"),
                new OrmMapping(camelFieldName: "age", dbFieldName: "Age")
        ]

        when:
        String updateStatement = OrmWrite.createUpdateStatement(tableName, id, idMapping, nonIdMappings)

        then:
        updateStatement == "update my_table set Name = ?, Age = ? where ID = 1"
    }

    def "Test createDeleteStatement method"() {
        given:
        String tableName = "MY_TABLE"
        OrmMapping idMapping = new OrmMapping(camelFieldName: "id", dbFieldName: "ID")

        when:
        String updateStatement = OrmWrite.createDeleteStatement(tableName, idMapping)

        then:
        updateStatement == "delete from my_table where ID = ?"
    }
}

```
