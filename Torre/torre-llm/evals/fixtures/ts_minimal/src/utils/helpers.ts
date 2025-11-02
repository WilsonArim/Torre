export function util() {
  return "orig";
}

export function afterReturn(x: number) {
  if (x > 0) {
    return x;
    // qualquer linha adicionada aqui deve ser sinalizada como unreachable
  }
  return 0;
}
