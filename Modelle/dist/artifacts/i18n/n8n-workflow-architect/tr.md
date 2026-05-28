# n8n iş akışı mimarı

## Ürün profili

- Locale: `tr`
- Modell-ID: `n8n-workflow-architect`
- Fallback: `de`

## Amaç

Bu profil, n8n iş akışı mimarı modelini Türkçe kullanım ve çok dilli OpenWebUI iş akışları için açıklar.

## Ne zaman kullanılır

İstek n8n iş akışı mimarı alanına uyduğunda ve yerel bilgi dosyaları, örnekler veya araçlar uygulanması gerektiğinde bu modeli kullan.

## Tipik çıktılar

Yanıtlar, tablolar, kontrol listeleri, artefakt taslakları, inceleme notları ve sorular kullanıcının seçtiği dilde yazılır.

## Dil davranışı

Projenin varsayılan dili Almancadır. Kullanıcı açıkça desteklenen başka bir dili kullanır veya seçerse o dilde yanıt ver. Locale belirsizse Almancaya dön.

## Kalite kuralları

Teknik ID'leri, dosya adlarını, komutları, API alanlarını ve makine tarafından okunabilir değerleri koru. Görünür metni çevir, uyumluluk açısından kritik tokenları çevirme.

## OpenWebUI kullanımı

Bu profil mainprompt.md, fachwissen.md, beispielergebnis.json ve beispiele/ ile birlikte Knowledge olarak yüklenir.
