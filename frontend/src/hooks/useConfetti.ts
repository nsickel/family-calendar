import confetti from "canvas-confetti";

export function useConfetti() {
  const fire = (x: number, y: number) => {
    confetti({
      particleCount: 80,
      spread: 60,
      origin: {
        x: x / window.innerWidth,
        y: y / window.innerHeight,
      },
      colors: ["#FF6B9D", "#4ECDC4", "#FFD93D", "#6BCB77", "#FF6B6B"],
      scalar: 1.2,
    });
  };
  return { fire };
}
