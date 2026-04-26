# 批量生成未绑定的 Keys
batch_generate_api_keys(admin_id=1, count=50, expires_days=365)

# 生成并绑定到指定用户
batch_generate_api_keys_with_users(admin_id=1, count=10, bind_users=True)
