import hashlib
import re
from typing import Optional, Dict


class UserAuthentication:
    """
    登录验证核心类
    功能：
    - 用户注册（密码加密存储）
    - 登录验证（账号密码校验）
    - 输入合法性校验
    - 错误信息提示
    """

    def __init__(self):
        # 模拟数据库存储用户信息（实际项目中替换为MySQL/Redis等）
        # 结构：{用户名: {密码哈希值, 盐值, 用户ID}}
        self.user_database: Dict[str, Dict[str, str]] = {}
        # 密码强度规则：至少8位，包含字母+数字
        self.password_pattern = re.compile(r'^(?=.*[A-Za-z])(?=.*\d).{8,}$')

    def _generate_salt(self) -> str:
        """生成随机盐值（用于密码加密）"""
        import os
        return os.urandom(16).hex()  # 生成16字节的随机盐值，转为16进制字符串

    def _encrypt_password(self, password: str, salt: str) -> str:
        """密码加密：使用SHA256 + 盐值（防止彩虹表攻击）"""
        # 拼接密码和盐值，然后加密
        password_salt = (password + salt).encode('utf-8')
        return hashlib.sha256(password_salt).hexdigest()

    def register_user(self, username: str, password: str) -> tuple[bool, str]:
        """
        用户注册（先校验，再加密存储）
        :param username: 用户名
        :param password: 原始密码
        :return: (是否成功, 提示信息)
        """
        # 1. 输入合法性校验
        if not username or len(username.strip()) == 0:
            return False, "用户名不能为空！"

        if username in self.user_database:
            return False, "用户名已存在！"

        if not self.password_pattern.match(password):
            return False, "密码不符合规则：至少8位，必须包含字母和数字！"

        # 2. 生成盐值和密码哈希
        salt = self._generate_salt()
        password_hash = self._encrypt_password(password, salt)

        # 3. 存储用户信息（模拟数据库写入）
        self.user_database[username] = {
            "password_hash": password_hash,
            "salt": salt,
            "user_id": str(len(self.user_database) + 1)  # 模拟用户ID自增
        }

        return True, f"用户 {username} 注册成功！"

    def login_verify(self, username: str, password: str) -> tuple[bool, str, Optional[str]]:
        """
        登录验证核心方法
        :param username: 输入的用户名
        :param password: 输入的原始密码
        :return: (是否成功, 提示信息, 用户ID/None)
        """
        # 1. 基础输入校验
        if not username or not password:
            return False, "用户名和密码不能为空！", None

        # 2. 检查用户是否存在
        if username not in self.user_database:
            return False, "用户名不存在！", None

        # 3. 密码校验（加密后对比）
        user_info = self.user_database[username]
        input_password_hash = self._encrypt_password(password, user_info["salt"])

        if input_password_hash == user_info["password_hash"]:
            return True, f"登录成功！欢迎 {username}", user_info["user_id"]
        else:
            return False, "密码错误！", None

    def get_user_info(self, username: str) -> Optional[Dict[str, str]]:
        """获取用户信息（仅演示，实际项目中需权限控制）"""
        return self.user_database.get(username, None)


# ==================== 使用示例 ====================
if __name__ == "__main__":
    # 初始化登录验证实例
    auth = UserAuthentication()

    # 1. 注册用户
    register_result, register_msg = auth.register_user("zhangsan", "Zhang123456")
    print(f"注册结果：{register_msg}")

    # 尝试注册重复用户名
    register_result2, register_msg2 = auth.register_user("zhangsan", "Li456789")
    print(f"注册结果：{register_msg2}")

    # 尝试注册弱密码
    register_result3, register_msg3 = auth.register_user("lisi", "123456")
    print(f"注册结果：{register_msg3}")

    # 2. 登录验证
    print("\n=== 登录测试 ===")
    # 正确密码登录
    login_success, login_msg, user_id = auth.login_verify("zhangsan", "Zhang123456")
    print(f"登录结果：{login_msg} | 用户ID：{user_id}")

    # 错误密码登录
    login_success2, login_msg2, user_id2 = auth.login_verify("zhangsan", "12345678")
    print(f"登录结果：{login_msg2} | 用户ID：{user_id2}")

    # 不存在的用户登录
    login_success3, login_msg3, user_id3 = auth.login_verify("wangwu", "Wang123456")
    print(f"登录结果：{login_msg3} | 用户ID：{user_id3}")