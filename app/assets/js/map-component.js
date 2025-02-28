function mapComponent() {
    return {
        map: null,
        
        async initMap() {
            try {
                console.log('Iniciando carga del mapa...');
                
                if (typeof google === 'undefined') {
                    console.error('Google Maps no está cargado');
                    return;
                }

                this.map = new google.maps.Map(document.getElementById('map'), {
                    ...MAP_CONFIG,
                    mapTypeControl: true,
                    streetViewControl: true,
                    fullscreenControl: true,
                    zoomControl: true
                });

                // Agregar marcador
                new google.maps.Marker({
                    position: MAP_CONFIG.center,
                    map: this.map,
                    title: "Punto Central"
                });

                console.log('Mapa cargado correctamente');
            } catch (error) {
                console.error('Error al cargar el mapa:', error);
            }
        },

        centerMap() {
            if (this.map) {
                this.map.setCenter(MAP_CONFIG.center);
            } else {
                console.error('El mapa no está inicializado');
            }
        }
    };
}
