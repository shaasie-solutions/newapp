# newapp

مستودع يضم تطبيق **Frappe / ERPNext** لإدارة الشحن بالشاحنات.

## المحتوى

| المسار | الوصف |
|--------|--------|
| [`haulage_mgmt/`](./haulage_mgmt/) | تطبيق Frappe كامل (`haulage_mgmt`) — راجع [**README التطبيق**](./haulage_mgmt/README.md) للتثبيت والإعداد. |

## البدء السريع

```bash
cd frappe-bench
bench get-app /path/to/clone/newapp/haulage_mgmt haulage_mgmt
bench --site yoursite.com install-app haulage_mgmt
bench migrate
```

التفاصيل الكاملة، تسلسل العمل، والإعدادات: **`haulage_mgmt/README.md`**.

## الإصدارات

يُستخدم [Semantic Versioning](https://semver.org/) عبر وسوم Git (مثال: `v0.1.0`).
