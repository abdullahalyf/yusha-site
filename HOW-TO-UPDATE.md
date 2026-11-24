# ইউশার সাইট — আপডেট করার নিয়ম

এই সাইট Vercel-এ চলে। GitHub-এ ফাইল বদলালেই কয়েক মিনিটে সাইট নিজে আপডেট হয়।

## লেখা বদলাতে
1. GitHub-এ নিজের repo খোলো → `personal` ফোল্ডার → `profile.yaml` → পেন্সিল (Edit) আইকন।
2. নাম, নতুন প্রজেক্ট, অ্যাচিভমেন্ট, ফোন, লিংক — যা বদলানো লাগে বদলাও। স্পেস (indent) ঠিক রাখো।
3. **Commit changes** চাপো। ২–৩ মিনিট পর সাইটে দেখা যাবে।

## ছবি বদলাতে
`personal/photos` ফোল্ডারে একই নামে নতুন ছবি আপলোড করো (Add file → Upload files):
- `profile.jpg` (বড় ছবি), `avatar.jpg` (ছোট গোল ছবি)
- `project-1.jpg`… (প্রজেক্টের ছবি, `profile.yaml`-এর ক্রম অনুযায়ী)
- `award-1.jpg`, `edu-1.jpg`, `hobby-1.jpg`
- `gallery/` ফোল্ডারে যত খুশি ছবি
- CV বদলাতে: `personal/cv.pdf`

## নতুন ব্লগ
`content/blog` → Add file → Create new file → নাম `my-post.md`। উপরে এভাবে লিখে নিচে লেখা দাও:
```
---
title: "শিরোনাম"
date: 2026-12-01
summary: "এক লাইনের সারাংশ"
cover: "my-post"
---
```
কভার ছবি: `personal/blog/my-post.jpg`।

## প্রথমবার চালু করতে
GitHub-এ এই repo Fork করো → vercel.com এ GitHub দিয়ে লগইন → Add New Project → তোমার fork বেছে Deploy চাপো (সেটিং বদলাতে হবে না)।
