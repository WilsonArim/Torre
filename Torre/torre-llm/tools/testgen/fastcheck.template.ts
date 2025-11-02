import fc from "fast-check";

import { $$FUNCTION$$ } from "$$MODULE$$";

test("property: $$FUNCTION$$ no throw", () => {
  fc.assert(
    fc.property(fc.anything(), (x:any) => {
      $$FUNCTION$$(x);
      return true;
    })
  );
});
