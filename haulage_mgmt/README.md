# haulage_mgmt — تطبيق لوجستيات الشحن لـ ERPNext

تطبيق **Frappe** يعتمد على **ERPNext** لإدارة طلبات الشحن بالشاحنات: أسطول، سائقون، مسارات، رحلات، مصروفات، فواتير بيع، وقيد يومية للمصروفات.

**الإصدار:** انظر `haulage_mgmt/__init__.py` ووسوم Git (مثل `v0.1.0`).

---

## المتطلبات

- [Frappe Bench](https://docs.frappe.io/framework/user/en/installation) مع موقع يعمل عليه **ERPNext**
- Python 3.10+ (حسب إصدار الـ bench لديك)

---

## التثبيت

انسخ المجلد `haulage_mgmt` داخل مجلد `apps` في الـ bench، أو أضفه كمصدر git:

```bash
cd /path/to/frappe-bench
bench get-app /path/to/newapp/haulage_mgmt haulage_mgmt
# أو: نسخ المجلد يدوياً ثم:
bench get-app ./apps/haulage_mgmt

bench --site yoursite.com install-app haulage_mgmt
bench --site yoursite.com migrate
bench build --app haulage_mgmt
```

بعد التثبيت، نفّذ **Migrate** عند كل تحديث للتطبيق.

---

## الإعداد الأولي

1. **Haulage Logistics Settings** (إعدادات لوجستيات الشحن)  
   - **صنف خدمة الشحن الافتراضي:** صنف `Item` (خدمة) يُستخدم في سطر فاتورة البيع عند زر «إنشاء فاتورة بيع للشحنة».  
   - **حساب دائن لترحيل مصروفات الرحلة:** حساب من دليل الحسابات (ليس من نوع Expense) لقيد يومية المصروفات.

2. **الأدوار**  
   - يُنشأ دور **Fleet Manager** تلقائياً عند `migrate`. عيّنه للمستخدمين من نموذج **User**.  
   - لزر «إنشاء قيد مصروفات»: يحتاج المستخدم صلاحية **إنشاء Journal Entry** (غالباً عبر **Role Permission Manager**).

3. **المجدول (Scheduler)**  
   - مهمة يومية للتذكير بوثائق الشاحنات/السائقين (مهام **ToDo**). تأكد من تشغيل `bench schedule` أو البيئة المعتادة لديك.

---

## تسلسل العمل المقترح

1. البيانات الأساسية: شاحنات، سائقون، خطوط سير، أنواع مصروفات (مع ربط حساب مصروف).  
2. **Customer** في ERPNext للعملاء.  
3. **Shipping Request** (طلب شحن).  
4. **Shipment Preparation** (تجهيز) حتى تصبح الشحنة جاهزة للرحلة.  
5. **Haulage Trip** (رحلة) مع ربط الشحنات والشاحنة والسائق والشركة.  
6. أحداث الرحلة، المصروفات، فاتورة البيع، قيد يومية المصروفات عند الحاجة.  
7. التقارير من وحدة **Haulage Logistics** أو من Workspace المكتب.

---

## المكوّنات الرئيسية

| نوع المستند / الميزة | الوصف |
|----------------------|--------|
| Truck, Driver | بيانات الأسطول والسائقين |
| Shipping Route | خطوط السير |
| Haulage Expense Type | أنواع مصروفات + ربط `Account` |
| Shipping Request | طلب شحن مرتبط بالعميل |
| Shipment Preparation | تجهيز الشحنة قبل الرحلة |
| Haulage Trip | رحلة تشغيل مع شحنات وأحداث ومصروفات |
| تقارير Script | Trip Financial Summary, Driver Performance, Truck Performance |
| Workspace | لوحة «إدارة الشحن» في Desk |
| لوحة العميل | ربط **Shipping Request** من بطاقة **Customer** |
| Print Format | Haulage Trip Dispatch |

---

## واجهات برمجية (Whitelisted)

- `haulage_mgmt.haulage_logistics.api.create_sales_invoice_from_shipment`  
- `haulage_mgmt.haulage_logistics.api.create_trip_expense_journal_entry`  

تُستدعى من أزرار نموذج **Haulage Trip** في الواجهة.

---

## الترخيص

انظر `license.txt` (MIT ما لم يُنص على غير ذلك).

---

## مراجع رسمية

- [Frappe Framework](https://docs.frappe.io/framework)  
- [ERPNext](https://docs.frappe.io/erpnext)  
- [Custom Apps](https://docs.frappe.io/erpnext/user/manual/en/customize-erpnext)
