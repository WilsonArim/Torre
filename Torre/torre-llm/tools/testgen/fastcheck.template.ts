/* eslint-disable import/no-unresolved */
import fc from "fast-check";

import { $$FUNCTION$$ } from "$$MODULE$$";

// eslint-disable-next-line no-undef
test("property: $$FUNCTION$$ no throw", () => {
  fc.assert(
    fc.property(fc.anything(), (x: unknown) => {
      // @ts-expect-error - Template file, function name will be replaced
      $$FUNCTION$$(x);
      return true;
    }),
  );
});
