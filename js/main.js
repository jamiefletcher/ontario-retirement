// Configuration
const CONFIG = {
    points: {
        file: 'data/homes.geojson',
        layers: [
            {
                beforeId: 'label-city',
                data: {
                    id: 'points',
                    type: 'circle',
                    source: 'points',
                    paint: {
                        'circle-color': 'hsl(26, 100%, 57%)',
                        'circle-radius': ["interpolate", ["linear"], ["zoom"], 5, 3, 20, 10],
                        'circle-stroke-width': ["interpolate", ["linear"], ["zoom"], 5, 1, 20, 2],
                        'circle-stroke-color': 'hsl(0, 0%, 100%)'
                    }
                }
            },
            {
                beforeId: 'points',
                data: {
                    id: 'points-blast-radius',
                    type: 'circle',
                    source: 'points',
                    paint: {
                        'circle-radius': 50,
                        'circle-color': 'hsl(26, 100%, 57%)',
                        'circle-opacity': 0.2,
                    },
                    minzoom: 13
                }
            }
        ]
    },
    lakes: {
        source: {
            id: 'ontario-lakes',
            type: 'vector',
            tiles: ['https://jamiefletcher.github.io/ontario-retirement/ontario-lakes/{z}/{x}/{y}.pbf'],
            tileSize: 512
        },
        layers: [
            {
                id: 'lakes',
                beforeId: null,
                data: {
                    type: 'fill',
                    source: 'ontario-lakes',
                    'source-layer': 'ontario-lakes',
                    paint: {
                        'fill-color': 'hsl(199, 78%, 80%)',
                        'fill-opacity': 1
                    },
                    minzoom: 5,
                    maxzoom: 8
                }
            }
        ]
    },
    styleFile: 'style.json',
    services: [
        "Bathing", "Hygiene", "Walking", "Feeding",
        "Wounds", "Continence", "Drugs", "Meals",
        "Dementia", "Dressing", "Pharmacist", "Doctor", "Nurse"
    ],
    markers: [
        'img/head_1.png', 'img/head_2.png', 'img/head_3.png', 'img/head_4.png',
        'img/head_5.png', 'img/head_6.png', 'img/head_7.png', 'img/head_8.png',
        'img/head_9.png'
    ],
    mapOptions: {
        container: 'map',
        style: 'style.json',
        hash: true,
        pixelRatio: 1,
        center: [-79.45, 43.75],
        zoom: 11,
        minZoom: 5,
        maxZoom: 18
    }
};

// DOM Elements
const dom = {
    mapContainer: document.getElementById('map'),
    searchInput: document.getElementById('search-input'),
    searchResults: document.getElementById('search-results'),
    filterHeader: document.getElementById('filter-header'),
    filterOptions: document.getElementById('filter-options')
};

// State
let allFeatures = [];
const map = new maplibregl.Map(CONFIG.mapOptions);

// Filters
function createServiceFilters() {
    const { filterOptions } = dom;
    const { services } = CONFIG;

    filterOptions.innerHTML = services.map(service => `
        <div class="filter-option">
        <label>
            <input type="checkbox" id="filter-${service}" value="${service}">
            ${service}
        </label>
        </div>
    `).join('');
}

function handleFilterHeaderClick(e, forceClose = false) {
    if (e && !forceClose) e.stopPropagation(); // This prevents the event from bubbling up to document
    const { filterHeader, filterOptions } = dom;
    const isHidden = forceClose ? false : filterOptions.style.display === 'none';
    filterOptions.style.display = isHidden ? 'flex' : 'none';
    filterHeader.querySelector('.toggle-icon').innerHTML = isHidden
        ? '<i class="fas fa-caret-up"></i>'
        : '<i class="fas fa-caret-down"></i>';
}

function updateFilteredData() {
    const checkboxes = document.querySelectorAll('#service-filters input[type="checkbox"]:checked');
    const activeFilters = Array.from(checkboxes).map(cb => cb.value);

    const filteredFeatures = activeFilters.length === 0
        ? allFeatures
        : allFeatures.filter(feature => {
            if (!feature.properties.services) return false;
            return activeFilters.every(service =>
                feature.properties.services[service] === true
            );
        });

    map.getSource('points').setData({
        type: 'FeatureCollection',
        features: filteredFeatures
    });
}

// Search
function handleSearch() {
    const searchTerm = dom.searchInput.value.toLowerCase();

    if (searchTerm.length < 2) {
        dom.searchResults.style.display = 'none';
        return;
    }

    const matches = allFeatures.filter(feature =>
        feature.properties.name.toLowerCase().includes(searchTerm)
    );

    displaySearchResults(matches);
}

function displaySearchResults(results) {
    dom.searchResults.innerHTML = '';
    dom.searchResults.style.display = 'block';
    if (!results.length) {
        dom.searchResults.innerHTML = '<div class="search-result">No matches found</div>';
        return;
    }
    dom.searchResults.innerHTML = results.map(feature => `
        <div class="search-result" data-feature-id="${feature.id || feature.properties.name}">
        ${feature.properties.name}
        </div>
    `).join('');
}

function handleSearchResultClick(e) {
    const resultElement = e.target.closest('.search-result');
    if (!resultElement) return;

    const featureId = resultElement.dataset.featureId;
    const feature = allFeatures.find(f =>
        (f.id || f.properties.name) === featureId
    );

    if (feature) {
        zoomToFeature(feature);
        createPopup(feature);
        dom.searchResults.style.display = 'none';
        dom.searchInput.value = '';
    }
}

// Popups
function createPopup(feature) {
    const { properties, geometry } = feature;
    const searchQuery = encodeURIComponent(`${properties.name} ${properties.streetaddress}`);
    const services = parseServices(properties.services);

    new maplibregl.Popup()
        .setLngLat(geometry.coordinates)
        .setHTML(`
        <div class="popup-container">
            <h2>${properties.name}</h2>
            ${createContactInfo(properties, searchQuery)}
            ${createCapacityInfo(properties)}
            ${createServicesGrid(services)}
        </div>
        `)
        .addTo(map);
}

// Helper Functions
function parseServices(services) {
    if (!services) return {};
    return typeof services === 'string' ? JSON.parse(services) : services;
}

function createContactInfo(properties, searchQuery) {
    return `
        <div class="contact-info">
        <div>
            <i class="fa-solid fa-location-dot"></i>
            <a href="https://www.google.com/maps/search/?api=1&query=${searchQuery}" target="_blank">
            ${properties.streetaddress}
            </a>
        </div>
        ${properties.phone_number ? `
            <div>
            <i class="fa-solid fa-phone"></i>
            <a href="tel:${properties.phone_number}">${properties.phone_number}</a>
            </div>
        ` : ''}
        ${properties.web_address ? `
            <div>
            <i class="fa-solid fa-globe"></i>
            <a href="${formatUrl(properties.web_address)}" class="ellipsis" target="_blank">
                ${properties.web_address}
            </a>
            </div>
        ` : ''}
        </div>
    `;
}

function formatUrl(url) {
    return url.startsWith('http') ? url : `https://${url}`;
}

function createCapacityInfo(properties) {
    return properties.number_of_suites || properties.resident_capacity ? `
        <div class="capacity">
        ${properties.number_of_suites ? `${properties.number_of_suites} rooms` : ''}
        ${properties.number_of_suites && properties.resident_capacity ? ' / ' : ''}
        ${properties.resident_capacity ? `${properties.resident_capacity} beds` : ''}
        </div>
    ` : '';
}

function createServicesGrid(services) {
    if (!services || !Object.keys(services).length) return '';

    return `
        <div class="services-grid">
        ${Object.entries(services).map(([service, available]) => `
            <div class="service-item">
            <span>
                ${available ? '<i class="fa-solid fa-check"></i>' : '<i class="fa-solid fa-xmark"></i>'}
                ${service}
            </span>
            </div>
        `).join('')}
        </div>
    `;
}

function zoomToFeature(feature) {
    map.flyTo({
        center: feature.geometry.coordinates,
        zoom: 16,
        essential: true
    });
}

// Initialize
createServiceFilters();
dom.searchInput.addEventListener('input', handleSearch);
dom.searchResults.addEventListener('click', handleSearchResultClick);
dom.filterHeader.addEventListener('click', (e) => handleFilterHeaderClick(e));
dom.filterOptions.addEventListener('change', updateFilteredData);

// Close search results when clicking elsewhere
document.addEventListener('click', (e) => {
    const { filterOptions, searchResults } = dom;

    // Close search results if clicking outside
    if (!e.target.closest('.search-container')) {
        searchResults.style.display = 'none';
    }

    // Close filters if clicking outside
    if (!e.target.closest('.filter-container') && filterOptions.style.display !== 'none') {
        handleFilterHeaderClick(null, true); // Force close
    }
});

map.on('load', () => {
    fetch(CONFIG.points.file)
        .then(response => response.json())
        .then(data => {
            allFeatures = data.features;

            // Add a random marker image index property to each feature
            allFeatures.forEach(feature => {
                feature.properties.markerId = Math.floor(Math.random() * 9); // 0-8
            });

            map.addSource('points', {
                type: 'geojson',
                data: data,
                cluster: false
            });

            CONFIG.points.layers.forEach(layer => {
                map.addLayer(layer.data, layer.beforeId);
            });

            map.on('click', 'points', (e) => {
                const feature = e.features[0];
                createPopup(feature);
            });

            map.on('mouseenter', 'points', () => {
                map.getCanvas().style.cursor = 'pointer';
            });
            map.on('mouseleave', 'points', () => {
                map.getCanvas().style.cursor = '';
            });
        });

    map.addSource(CONFIG.lakes.source.id, CONFIG.lakes.source);
    CONFIG.lakes.layers.forEach(layer => {
        map.addLayer({ ...layer.data, id: layer.id }, layer.beforeId);
    });
});