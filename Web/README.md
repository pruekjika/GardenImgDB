this is my first time pull image from github folder
it have limit to Rate-limits (up to `60 per-hour` for anonymous, up to 5,000 per-hour for authenticated)

[How to get a file via GitHub APIs - Stack Overflow](https://stackoverflow.com/questions/9272535/how-to-get-a-file-via-github-apis)

need to do authenticated to make it more stable by

1.  create `.env` file and add line below to pc

```
VITE_GITHUB_ACCESS_TOKEN={{token}}
```

2. and add github secret in github

3. ยังคงการเรียก header ตามด้านล่าง

```tsx
const response = await fetch(
  `https://api.github.com/repos/${owner}/${repo}/contents/ImageDB/Fixed/`,
  {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  }
);
```

4. ให้ทำการ build vite ผ่าน github action โดย ทำตามนี้

   [Deploying a Vite app on GitHub Pages using GitHub Actions with GitHub Secrets - DEV Community](https://dev.to/dwtoledo/deploying-a-vite-app-on-github-pages-using-github-actions-with-github-secrets-1hn0)
