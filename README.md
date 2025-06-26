# django-js-pretty

A simple script and pre-commit hook to format JavaScript code in Django projects.
Uses [jsbeautifier](https://beautifier.io/) under the hood, but prevents it from mangling Django template tags.


### Using django-js-pretty with pre-commit

To run django-js-pretty via pre-commit, add the following to your `.pre-commit-config.yaml`:

```yaml
repos:
- repo: https://github.com/pkasprzyk/django-js-pretty
  rev: v0.1.0
  hooks:
    - id: django-js-pretty
```

### Excluding paths from pre-commit hook

To exclude files or directories when using django-js-pretty with pre-commit, use the `exclude` option.
By default, it excludes `node_modules` and any `.min.js` files. You can customize this to fit your needs.

```yaml
repos:
- repo: https://github.com/pkasprzyk/django-js-pretty
  rev: v0.1.0
  hooks:
    - id: django-js-pretty
      exclude: "(^node_modules/)|(.*.min.js$)|(assets/js/.*.js$)"
```
