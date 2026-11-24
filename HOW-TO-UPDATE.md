# ইউশার ওয়েবসাইট — চালু করা ও আপডেট করার নিয়ম

## ১. Vercel-এ চালু করা (একবারই)
1. GitHub-এ লগইন করে https://github.com/abdullahalyf/yusha-site খোলো → উপরে ডানে **Fork** → **Create fork**।
2. https://vercel.com এ গিয়ে **Continue with GitHub** দিয়ে লগইন করো।
3. **Add New… → Project** → তালিকায় `yusha-site` এর পাশে **Import**।
4. কোনো সেটিং বদলাবে না। সরাসরি **Deploy** চাপো। ১–২ মিনিট পর লিংক পাবে (যেমন `yusha-site.vercel.app`)।

ফর্ক না করে চাইলে: repo-র **Code → Download ZIP** নামিয়ে, নিজের GitHub-এ নতুন repo বানিয়ে সব ফাইল আপলোড করো (একবারে সর্বোচ্চ ১০০টা ফাইল), তারপর উপরের ২–৪ ধাপ।

## ২. আপডেট করা
GitHub-এ কোনো ফাইল বদলে **Commit changes** চাপলেই Vercel ২–৩ মিনিটে সাইট নিজে আপডেট করে।

**লেখা বদলাতে:** `personal/profile.yaml` → পেন্সিল (Edit) আইকন। নাম, প্রজেক্ট, অ্যাচিভমেন্ট, ফোন, লিংক, Work পেজ (`work:`), হোমের "Open to…" লাইন (`open_to:`) সব এখানে। লাইনের শুরুর স্পেস (indent) যেমন আছে তেমন রাখবে।

**ছবি বদলাতে:** `personal/photos/` ফোল্ডারে **একই নামে** নতুন ছবি আপলোড করো (Add file → Upload files):
- `profile.jpg` বড় ছবি, `avatar.jpg` গোল ছবি
- `project-1.jpg`, `project-2.jpg`… প্রজেক্টের ক্রম অনুযায়ী
- `award-1.jpg`, `edu-1.jpg`, `hobby-1.jpg`…
- `gallery/` ফোল্ডারে যত খুশি ছবি
- `work/plant-1.jpg`…`plant-4.jpg` গাছের ব্যবসার ছবি

**CV বদলাতে:** `personal/cv.pdf` (মূল CV) আর `personal/cv-tutor.pdf` (টিউটর CV) একই নামে আপলোড করো।

**নতুন ব্লগ:** `content/blog` → Add file → Create new file → নাম `my-post.md`। উপরে এটা লিখে নিচে লেখা দাও:
```
---
title: "শিরোনাম"
date: 2026-12-01
summary: "এক লাইনের সারাংশ"
cover: "my-post"
---
```
কভার ছবি `personal/blog/my-post.jpg` নামে আপলোড করো।

## কিছু ভেঙে গেলে
Vercel-এর Deployments পেজে লাল দাগ দেখলে শেষ যে ফাইল বদলেছ সেটা আগের মতো করে দাও। সাধারণত `profile.yaml`-এ স্পেস বা উদ্ধৃতিচিহ্ন (") ভুল হলেই এমন হয়।
