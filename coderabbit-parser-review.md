# CodeRabbit Review: `src/asyncload/parser.py`

## Status

CodeRabbit review could not be completed.

## Requested Scope

- File: `src/asyncload/parser.py`

## Failure

The CodeRabbit CLI is not installed in this environment.

Command attempted:

```powershell
coderabbit --version
```

Result:

```text
coderabbit : The term 'coderabbit' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

Per the CodeRabbit workflow, I then attempted to install the CLI:

```powershell
curl -fsSL https://cli.coderabbit.ai/install.sh | sh
```

Result:

```text
sh : The term 'sh' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

## Resolution Needed

Install and authenticate the CodeRabbit CLI in a supported shell, then rerun the review.

On Windows, CodeRabbit's CLI documentation says WSL is required. From WSL, run:

```bash
curl -fsSL https://cli.coderabbit.ai/install.sh | sh
coderabbit auth login --agent
coderabbit auth status --agent
```

After that, rerun:

```bash
coderabbit review --agent
```

## CodeRabbit Issues

CodeRabbit raised 0 issues because the review did not run.

No manual review findings are included here, so this report does not misrepresent non-CodeRabbit feedback as CodeRabbit output.
