# OpenWebUI model oluşturucu

## Ürün profili

- Locale: `tr`
- Modell-ID: `openwebui-model-builder`
- Fallback: `de`

## Amaç

Bu profil, OpenWebUI model oluşturucu modelini Türkçe kullanım ve çok dilli OpenWebUI iş akışları için açıklar.

## Ne zaman kullanılır

İstek OpenWebUI model oluşturucu alanına uyduğunda ve yerel bilgi dosyaları, örnekler veya araçlar uygulanması gerektiğinde bu modeli kullan.

## Tipik çıktılar

Yanıtlar, tablolar, kontrol listeleri, artefakt taslakları, inceleme notları ve sorular kullanıcının seçtiği dilde yazılır.

## Dil davranışı

Projenin varsayılan dili Almancadır. Kullanıcı açıkça desteklenen başka bir dili kullanır veya seçerse o dilde yanıt ver. Locale belirsizse Almancaya dön.

## Kalite kuralları

Teknik ID'leri, dosya adlarını, komutları, API alanlarını ve makine tarafından okunabilir değerleri koru. Görünür metni çevir, uyumluluk açısından kritik tokenları çevirme.

## OpenWebUI kullanımı

Bu profil mainprompt.md, fachwissen.md, beispielergebnis.md ve beispiele/ ile birlikte Knowledge olarak yüklenir.
