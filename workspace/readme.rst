class PermissionEnum(enum.Enum):
    CreateTable = Permission(
        id="CreateTable",
        resource_type="DATABASE",
        permission="CREATE_DATABASE",
        grantable=False,
    )

    AlterDatabase = Permission(
        id="AlterDatabase",
        resource_type="DATABASE",
        permission="ALTER",
        grantable=False,
    )

    DropDatabase = Permission(
        id="DropDatabase",
        resource_type="DATABASE",
        permission="DROP",
        grantable=False,
    )

    DescribeDatabase = Permission(
        id="DescribeDatabase",
        resource_type="DATABASE",
        permission="DESCRIBE",
        grantable=False,
    )

    SuperDatabase = Permission(
        id="SuperDatabase",
        resource_type="DATABASE",
        permission="ALL",
        grantable=False,
    )

    CreateTableGrantable = Permission(
        id="CreateTableGrantable",
        resource_type="DATABASE",
        permission="CREATE_DATABASE",
        grantable=True,
    )

    AlterDatabaseGrantable = Permission(
        id="AlterDatabaseGrantable",
        resource_type="DATABASE",
        permission="ALTER",
        grantable=True,
    )

    DropDatabaseGrantable = Permission(
        id="DropDatabaseGrantable",
        resource_type="DATABASE",
        permission="DROP",
        grantable=True,
    )

    DescribeDatabaseGrantable = Permission(
        id="DescribeDatabaseGrantable",
        resource_type="DATABASE",
        permission="DESCRIBE",
        grantable=True,
    )

    SuperDatabaseGrantable = Permission(
        id="SuperDatabaseGrantable",
        resource_type="DATABASE",
        permission="ALL",
        grantable=True,
    )

    Select = Permission(
        Select="SELECT_TABLE",
        resource_type="TABLE",
        permission="SELECT",
        grantable=False,
    )

    Insert = Permission(
        Insert="INSERT_TABLE",
        resource_type="TABLE",
        permission="INSERT",
        grantable=False,
    )

    Delete = Permission(
        Delete="DELETE_TABLE",
        resource_type="TABLE",
        permission="DELETE",
        grantable=False,
    )

    DescribeTable = Permission(
        id="DescribeTable",
        resource_type="TABLE",
        permission="DESCRIBE",
        grantable=False,
    )

    AlterTable = Permission(
        id="AlterTable",
        resource_type="TABLE",
        permission="ALTER",
        grantable=False,
    )

    DropTable = Permission(
        id="DropTable",
        resource_type="TABLE",
        permission="DROP",
        grantable=False,
    )

    SuperTable = Permission(
        id="SuperTable",
        resource_type="TABLE",
        permission="ALL",
        grantable=False,
    )

    SelectGrantable = Permission(
        id="SelectGrantable",
        resource_type="TABLE",
        permission="SELECT",
        grantable=True,
    )

    InsertGrantable = Permission(
        id="InsertGrantable",
        resource_type="TABLE",
        permission="INSERT",
        grantable=True,
    )

    DeleteGrantable = Permission(
        id="DeleteGrantable",
        resource_type="TABLE",
        permission="DELETE",
        grantable=True,
    )

    DescribeTableGrantable = Permission(
        id="DescribeTableGrantable",
        resource_type="TABLE",
        permission="DESCRIBE",
        grantable=True,
    )

    AlterTableGrantable = Permission(
        id="AlterTableGrantable",
        resource_type="TABLE",
        permission="ALTER",
        grantable=True,
    )

    DropTableGrantable = Permission(
        id="DropTableGrantable",
        resource_type="TABLE",
        permission="DROP",
        grantable=True,
    )

    SuperTableGrantable = Permission(
        id="SuperTableGrantable",
        resource_type="TABLE",
        permission="ALL",
        grantable=True,
    )