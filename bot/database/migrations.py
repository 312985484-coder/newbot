"""
数据库迁移脚本
"""

from sqlalchemy import text

from bot.database.connection import engine, Base


def run_migrations():
    """运行数据库迁移"""
    from bot.database.models import (
        User, Report, ReportedUser, Appeal,
        Advertisement, GroupSettings, ApiKey
    )

    print("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成!")


def drop_all_tables():
    """删除所有表（危险操作）"""
    confirm = input("确定要删除所有表吗? 此操作不可撤销! (yes/no): ")
    if confirm.lower() == "yes":
        Base.metadata.drop_all(bind=engine)
        print("所有表已删除")
    else:
        print("操作已取消")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        drop_all_tables()
    else:
        run_migrations()