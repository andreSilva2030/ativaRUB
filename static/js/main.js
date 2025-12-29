document.addEventListener("DOMContentLoaded", () => {
    // Adicionar animação de fade-in ao carregar os cartões
    const cards = document.querySelectorAll(".card");
    cards.forEach((card, index) => {
        card.style.opacity = 0;
        card.style.transform = "translateY(20px)";
        setTimeout(() => {
            card.style.transition = "opacity 0.5s ease, transform 0.5s ease";
            card.style.opacity = 1;
            card.style.transform = "translateY(0)";
        }, index * 100); // Delay para cada cartão
    });

    // Adicionar animação ao clicar nos botões
    const buttons = document.querySelectorAll(".btn");
    buttons.forEach((button) => {
        button.addEventListener("click", () => {
            button.style.transform = "scale(0.9)";
            setTimeout(() => {
                button.style.transform = "scale(1)";
            }, 150);
        });
    });
});