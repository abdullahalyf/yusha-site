---
title: "Building StockSync in C"
date: 2026-11-17
summary: "Notes on my warehouse inventory program for the CSE214 Algorithm Lab."
tags: ["c", "projects"]
cover: "building-stocksync"
---

StockSync is a warehouse inventory program in C, built for the CSE214 Algorithm Lab at DIU. You run it in the terminal and pick what you want from a menu.

## What it does

You can add, view, edit and remove products, record stock in and out, search, and sort the list. It also gives a dashboard summary, a low-stock report, category and supplier value reports, and an activity history. Data can be saved, backed up and exported to CSV.

## What I learned

A menu program looks simple, but every option needs its own checks: what if the product does not exist, or the quantity is negative? Sorting and searching gave me a reason to use the algorithms from class on data that felt real.

## Next

I want to clean up the code, split it into smaller files and try the same idea in Java. The code is on my GitHub.
