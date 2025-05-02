# Magplan

Project management system for publishers, magazines and content creators, written on the top of Django Framework.

## Features

* complete posts management: from article idea to publishing;
* articles stages, assignees, roles;
* posts metadata, editors, authors, attachments (images, PDF's, files);
* extendable Markdown engine with ability to use external one;
* posts ideas with voting system;
* discussions, email notifications;
* team actions logs;
* publish content to S3 and WordPress with async tasks.

![](docs/screenshot1.jpg)

##  Development

This project uses uv for dependency management. Make sure you have uv installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Run development

This will install development dependencies:

```bash
make devel
```

## Publish a New Version

To create a new version, follow these steps:

1. Make sure all your changes are committed.

2. Run one of the following commands to bump the version in pyproject.toml:

For a major version bump (e.g., 1.0.0 -> 2.0.0)
```bash
make bump-version TYPE=major
```

For a minor version bump (e.g., 1.0.0 -> 1.1.0)
```bash
make bump-version TYPE=minor
```

For a patch version bump (e.g., 1.0.0 -> 1.0.1)
```bash
make bump-version TYPE=patch
```

**Commit the changes to the repository.*

3. Create a git tag with the new version:
```bash
make create-tag
```

4. Push the changes and new tag to trigger the CI/CD pipeline:
```bash
git push origin
git push origin --tags
```

The CI/CD pipeline will automatically build and deploy the new version when it detects the new tag.

### Version Number Format

- **MAJOR**: Incremented for incompatible API changes
- **MINOR**: Incremented for backward-compatible functionality additions
- **PATCH**: Incremented for backward-compatible bug fixes

### Current Version

The current version can be checked by running:
```bash
grep 'version = ' pyproject.toml
```

## LICENSE

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.