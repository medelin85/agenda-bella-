// Apenas conveniência no cliente. O servidor repete todas as validações.
const locationField = document.querySelector('#location');
const addressField = document.querySelector('#address');
if (locationField && addressField) {
  const update = () => { addressField.required = locationField.value === 'domiciliar'; };
  locationField.addEventListener('change', update);
  update();
}
