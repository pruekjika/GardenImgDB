this is my first time pull image from github folder
it have limit to Rate-limits (up to `60 per-hour` for anonymous, up to 5,000 per-hour for authenticated) read more

[How to get a file via GitHub APIs - Stack Overflow](https://stackoverflow.com/questions/9272535/how-to-get-a-file-via-github-apis)

need to do authenticated to make it more stable by

create `.env` file and add line below to pc

```
VITE_GITHUB_ACCESS_TOKEN={{token}}
```

and add github secret

สรุปเรื่อง token คือ เหมือนว่าถ้าทำตาม
[Authenticating to the REST API - GitHub Docs](https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api?apiVersion=2022-11-28)
ด้วยการเพิ่ม workflow อันนี้

```yaml
name: CI

on:
  push:
    branches:
      - main

jobs:
  use_api:
    runs-on: ubuntu-latest
    permissions: {}
    steps:
      - env:
          GH_TOKEN: ${{ secrets.VITE_GITHUB_ACCESS_TOKEN }}
        run: |
          curl --request GET \
          --url "https://api.github.com/repos/pruekjika/GardenImgDB/contents/ImageDB/Fixed/" \
          --header "Authorization: Bearer $GH_TOKEN"
```

เราจะไม่ต้องเรียกอะไรพิเศษ ตอน fetch ใน script แล้ว
พระเจ้า เข้าใจยากมากๆเลย
