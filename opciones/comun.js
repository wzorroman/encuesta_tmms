const form = document.getElementById('form-encuesta');
const btnEnviar = document.getElementById('btn-enviar');
const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
const barra = document.getElementById('barra-progreso');
const texto = document.getElementById('progreso-texto');

function actualizar() {
    const items = document.querySelectorAll('.pregunta-card');
    const respondidas = Array.from(items).filter(el =>
        el.querySelectorAll('input[type="radio"]:checked').length > 0
    ).length;
    if (barra) barra.style.width = (respondidas / items.length * 100) + '%';
    if (texto) texto.textContent = respondidas + ' / ' + items.length;
}

document.querySelectorAll('input[type="radio"]').forEach(r => {
    r.addEventListener('change', function () {
        actualizar();
        const card = this.closest('.pregunta-card');
        if (card && card.classList.contains('is-invalid') &&
            card.querySelectorAll('input[type="radio"]:checked').length > 0) {
            card.classList.remove('is-invalid');
        }
    });
});

btnEnviar.addEventListener('click', function () {
    form.classList.add('was-validated');
    const sinResponder = Array.from(document.querySelectorAll('.pregunta-card')).filter(el =>
        el.querySelectorAll('input[type="radio"]:checked').length === 0
    );
    sinResponder.forEach(el => el.classList.add('is-invalid'));
    if (sinResponder.length === 0) {
        confirmModal.show();
    } else {
        sinResponder[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
});
