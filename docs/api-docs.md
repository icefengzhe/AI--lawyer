# AI Lawyer API 文档

## 认证 API

### 用户注册
**POST** `/api/register`

注册新用户并返回访问令牌。

请求体:
```json
{
    "username": "string",
    "email": "string",
    "password": "string"
}
```

响应:
```json
{
    "access_token": "string",
    "token_type": "bearer"
}
```

### 用户登录
**POST** `/api/token`

验证用户凭据并返回访问令牌。

请求体:
```form-data
username: string
password: string
```

响应:
```json
{
    "access_token": "string",
    "token_type": "bearer"
}
```

## 认证要求

除了登录和注册接口外，所有API请求都需要在Header中包含Bearer Token:

```
Authorization: Bearer <access_token>
```

## 错误响应

所有API错误响应的格式如下:

```json
{
    "detail": "错误信息描述"
}
```

常见HTTP状态码:
- 400: 请求参数错误
- 401: 未认证或认证失败
- 403: 权限不足
- 404: 资源不存在
- 500: 服务器内部错误 