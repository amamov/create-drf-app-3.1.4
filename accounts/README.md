# [JWT (Json Web Token)](https://jwt.io/)

## JWT Authenticate Process

1. frontend : id와 password를 body에 담아 backend에게 request한다.

2. backend : id와 password를 검증하고 `AccessToken`, `RefreshToken`를 body에 담아 response한다.
    - `RefreshToken`은 DB에 저장한다.

3. frontend : `AccessToken`와 `RefreshToken`은 안전한 곳에 보관하고 permission이 필요한 api에 `AccessToken`를 header에 같이 붙여서 request한다.

4. backend : `AccessToken`이 유효한지 체크한다. 유효하지 않다면 401 response를 보낸다.

5. frontend : 만약 `AccessToken`이 만료되어 authentication이 실패하였다면, 재발급을 위해 `AccessToken`와 `RefreshToken`을 body에 넣어서 refresh api를 request한다.

6. backend : refresh api 요청이 들어오면, 요청한 `RefreshToken`이 현재 DB에 있는 것과 같은지 비교하고, 맞다면 `AccessToken`와 `RefreshToken`을 새로 발급하여 response한다.
    - 새로 발급한 `RefreshToken`은 DB에 업데이트한다.

7. frontend : 발급 받은 `AccessToken`를 사용한다.


> 위의 과정은 불필요한 api 요청이 발생한다. 따라서 이를 보완하기 위해 frontend애서 `AccessToken`의 만료시간을 계산해서 적절히 backend에 요청한다.
>  - 계산을 위해 2번 과정에서 backend는  `AccessToken`의 만료시간(timestamp)도 함께 담아 응답한다.


---

## JWT Structure

JWT is divided into Header, Payload, and Signature, and each part is separated by `.`
Each part is all base64 encoded and used.

### Header

```json
{
    "typ" : "JWT",
    "alg" : "HSA256"
}
```
- typ : 데이터 타입
- alg : 해쉬 알고리즘. 서명 부분을 암호화하는데 쓰인다.

### Payload

> Claim : Payload에 들어갈 정보들
 
- [registered claim](https://tools.ietf.org/html/rfc7519#section-4.1)
  - 사전 정의되어 있고 필수적으로 사용할 필요는 없지만 강력하게 사용이 권고되는 것들
  - `iss` : 이 데이터의 발행자
  - `iat` : 이 데이터가 발행된 시간
  - `exp` : 이 데이터가 만료된 시간
  - `sub` : 토큰의 제목
  - `aud` : 토큰의 대상
  - `nbf` : 토큰이 처리되지 않아야 할 시점. 이 시점이 지나기 전엔 토큰이 처리되지 않는다.
  - `jti` : 토큰의 고유 식별자  
- [public claims](https://www.iana.org/assignments/jwt/jwt.xhtml) 
- private claims



### Signature

> 토큰을 안전하게 확인한다. 

```js
// example

HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret)
```

