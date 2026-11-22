# Contributing

1. Create a focused branch for the change.
2. Keep business rules explicit and document any new calculation or assumption.
3. Add tests for normal cases, boundary conditions and invalid input.
4. Run `python -m unittest discover -s tests -v` before opening a pull request.
5. Avoid adding runtime dependencies unless the benefit is clear and the dependency is maintained.

For changes to inventory policy, include a worked numerical example in `docs/methodology.md` so that a reviewer can independently verify the calculation.
