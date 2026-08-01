# Implementation Guide

## Order

Identify facts → separate entities → choose stable keys → draw cardinalities → list constraints → normalize → review API fields → freeze v1 → hand off.

## Role rules

Core entities: users, user_preferences, destinations, hotels, restaurants, attractions, transport_options, trips, trip_members, itineraries, itinerary_days, itinerary_items, expenses, budget_allocations, saved_trips, reviews, AI conversations/messages, weather_snapshots, packing_items, activity_preferences. Record PK, FK, nullability, domain, default, unique/check rules and delete behavior.

For every increment: define input/output and errors → implement smallest slice → test valid/invalid input → integrate with one adjacent layer → document result → commit. Mark unfinished production paths with `TODO` and never claim a template is complete.
