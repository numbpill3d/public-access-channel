/*
 * NHI Digital Pet Widget — Morrowind/Occult/NHI Low-Poly Companion
 * Compact embeddable module for nolove.neocities.org
 *
 * Usage (standalone with auto Three.js load):
 *   <div id="nhi-pet"></div>
 *   <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
 *   <script src="nhi_pet.js"></script>
 *   <script>
 *     var pet = new NHIPet('#nhi-pet');
 *   </script>
 *
 * Requires: Three.js r128+ (already loaded on nolove.neocities.org)
 * License: MIT
 */

(function(global) {
    'use strict';

    // ═══ Mood definitions — Morrowind/occult/NHI color palette ═══
    var MOODS = {
        idle:      { color: 0x8b008b, eyeColor: 0x4b0082, runeColor: 0x4b0082, pulseSpeed: 0.5,  floatSpeed: 0.3, label: 'Dormant' },
        curious:   { color: 0xda70d6, eyeColor: 0xda70d6, runeColor: 0xda70d6, pulseSpeed: 1.2,  floatSpeed: 0.8, label: 'Observing' },
        happy:     { color: 0xff69b4, eyeColor: 0xff69b4, runeColor: 0xff69b4, pulseSpeed: 2.0,  floatSpeed: 1.0, label: 'Content' },
        excited:   { color: 0xff0000, eyeColor: 0xff0066, runeColor: 0xff0066, pulseSpeed: 4.0,  floatSpeed: 2.0, label: 'Ecstatic' },
        sleepy:    { color: 0x666666, eyeColor: 0x333333, runeColor: 0x555555, pulseSpeed: 0.2,  floatSpeed: 0.1, label: 'Resting' },
        hungry:    { color: 0x8b4513, eyeColor: 0xa0522d, runeColor: 0x8b4513, pulseSpeed: 1.5,  floatSpeed: 0.5, label: 'Starving' },
    };

    // ═══ Low-poly NHI creature ═══
    function NHIPet(containerSelector, options) {
        options = options || {};
        this.opts = options;

        this.container = (typeof containerSelector === 'string')
            ? document.querySelector(containerSelector)
            : containerSelector;

        if (!this.container) {
            console.error('[NHIPet] Container not found:', containerSelector);
            return;
        }

        this.container.style.position = 'relative';
        this.container.style.overflow = 'hidden';

        this.width = this.container.clientWidth;
        this.height = this.container.clientHeight;

        // State
        this.mood = 'idle';
        this.moodTimer = 0;
        this.lastInteraction = Date.now();
        this.hungerThreshold = 30000;  // 30s → sleepy
        this.starveThreshold = 60000;  // 60s → hungry
        this.mouseX = 0;
        this.mouseY = 0;
        this.mouseNear = false;

        this._initScene();
    }

    // ═══ Scene initialization ═══
    NHIPet.prototype._initScene = function() {
        var THREE = global.THREE;
        var w = this.width, h = this.height;

        // Scene (transparent background for embedding)
        this.scene = new THREE.Scene();

        // Camera — isometric view
        this.camera = new THREE.PerspectiveCamera(30, w / h, 0.1, 1000);
        this.camera.position.set(0, 1.5, 4);
        this.camera.lookAt(0, 0, 0);

        // Renderer
        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true,
            powerPreference: 'low-power'
        });
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.setSize(w, h);
        this.container.appendChild(this.renderer.domElement);

        // Lighting — purple-tinted (Morrowind/occult/NHI palette)
        var ambient = new THREE.AmbientLight(0x404040, 1.2);
        this.scene.add(ambient);

        var dirLight = new THREE.DirectionalLight(0xff69b4, 0.6);
        dirLight.position.set(3, 5, 3);
        this.scene.add(dirLight);

        var rimLight = new THREE.DirectionalLight(0x8b008b, 0.4);
        rimLight.position.set(-3, -2, -3);
        this.scene.add(rimLight);

        // Container group for all pet parts
        this.petGroup = new THREE.Group();
        this.scene.add(this.petGroup);

        this._createPet();
        this._bindEvents();
        this._animate();

        // Resize handling
        var self = this;
        window.addEventListener('resize', function() {
            self.width = self.container.clientWidth;
            self.height = self.container.clientHeight;
            self.camera.aspect = self.width / self.height;
            self.camera.updateProjectionMatrix();
            self.renderer.setSize(self.width, self.height);
        });
    };

    // ═══ Build the low-poly NHI creature ═══
    NHIPet.prototype._createPet = function() {
        var THREE = global.THREE;
        var mood = MOODS[this.mood];

        // ═══ BODY — low-poly icosphere, stretched for elongated NHI silhouette ═══
        var bodyGeo = new THREE.IcosahedronGeometry(0.8, 1, 2);
        bodyGeo.scale(1, 1.4, 0.7);
        var bodyMat = new THREE.MeshBasicMaterial({
            color: mood.color,
            flatShading: true,
        });
        this.body = new THREE.Mesh(bodyGeo, bodyMat);
        this.petGroup.add(this.body);

        // ═══ CORE ORB — glowing central sphere (NHI bio-luminescence) ═══
        var coreGeo = new THREE.IcosahedronGeometry(0.25, 1, 1);
        this.coreMat = new THREE.MeshBasicMaterial({
            color: 0xff0000,
            transparent: true,
            opacity: 0.9,
        });
        this.core = new THREE.Mesh(coreGeo, this.coreMat);
        this.core.position.set(0, 0.3, 0);
        this.body.add(this.core);

        // ═══ EYES — 3 floating orbs (NHI has no face, just eye-sensors) ═══
        this.eyes = [];
        var eyeGeo = new THREE.SphereGeometry(0.18, 8, 6);
        var eyeOffsets = [
            { x: -0.35, y: 0.35, z: 0.55 },   // left
            { x:  0.35, y: 0.35, z: 0.55 },   // right
            { x:     0, y: 0.45, z: 0.40 },   // center (unhumanlike)
        ];
        for (var i = 0; i < 3; i++) {
            var eyeMat = new THREE.MeshBasicMaterial({
                color: mood.eyeColor,
                transparent: true,
                opacity: 0.85,
            });
            var eye = new THREE.Mesh(eyeGeo, eyeMat);
            eye.position.set(eyeOffsets[i].x, eyeOffsets[i].y, eyeOffsets[i].z);
            this.eyes.push({
                mesh: eye,
                offset: eyeOffsets[i],
                blinkPhase: Math.random() * Math.PI * 2,
            });
            this.body.add(eye);
        }

        // ═══ TENTACLE-LIMBS — thin cone appendages ═══
        this.tentacles = [];
        var tentGeo = new THREE.ConeGeometry(0.08, 1.2, 5, 1);
        for (var j = 0; j < 4; j++) {
            var t = new THREE.Mesh(tentGeo, bodyMat.clone());
            var angle = (j / 4) * Math.PI * 2;
            t.position.set(Math.cos(angle) * 0.55, -0.5, Math.sin(angle) * 0.55);
            t.rotation.z = angle + Math.PI / 2;
            this.tentacles.push({ mesh: t, baseAngle: angle });
            this.body.add(t);
        }

        // ═══ ANTENNAE — spires with glowing tips ═══
        this.antennae = [];
        var antenGeo = new THREE.CylinderGeometry(0.03, 0.03, 1.0, 6);
        for (var k = -1; k <= 1; k += 2) {
            var a = new THREE.Mesh(antenGeo, new THREE.MeshBasicMaterial({
                color: 0x8b008b,
                wireframe: true,
                transparent: true,
                opacity: 0.7,
            }));
            a.position.set(k * 0.35, 0.9, 0);
            a.rotation.z = k * 0.3;

            // Glowing tip orb
            var tipGeo = new THREE.IcosahedronGeometry(0.12, 0, 1);
            var tipMat = new THREE.MeshBasicMaterial({
                color: 0xff69b4,
                transparent: true,
                opacity: 0.9,
            });
            var tip = new THREE.Mesh(tipGeo, tipMat);
            tip.position.y = 0.5;
            a.add(tip);

            this.antennae.push({ mesh: a, tip: tip });
            this.body.add(a);
        }

        // ═══ RUNE SIGNS — floating translucent sigils (occult/NHI) ═══
        this.runes = [];
        for (var r = 0; r < 6; r++) {
            var rune = this._createRune(mood.runeColor);
            var rAngle = (r / 6) * Math.PI * 2;
            var rRadius = 1.3 + Math.random() * 0.3;
            rune.position.set(
                Math.cos(rAngle) * rRadius,
                Math.sin(rAngle * 0.7) * 0.5,
                Math.sin(rAngle) * rRadius
            );
            rune.userData = { phase: Math.random() * Math.PI * 2, radius: rRadius };
            this.petGroup.add(rune);
            this.runes.push(rune);
        }

        // ═══ ASH PARTICLES — Morrowind ash drift ═══
        this._createAshParticles();
    };

    // Create a low-poly rune sigil
    NHIPet.prototype._createRune = function(color) {
        var THREE = global.THREE;
        var geo = new THREE.BufferGeometry();
        var verts = new Float32Array([
            -0.15, -0.15, 0,  0.15, -0.15, 0,  0, 0.15, 0,
            -0.05, 0.02, 0,   0.05, 0.02, 0,  0, -0.02, 0,
        ]);
        var indices = [0, 2, 1, 3, 5, 4, 3, 4, 5];
        geo.setAttribute('position', new THREE.BufferAttribute(verts, 3));
        geo.setIndex(indices);
        var mat = new THREE.MeshBasicMaterial({
            color: color,
            transparent: true,
            opacity: 0.4,
            wireframe: true,
            depthWrite: false,
        });
        return new THREE.Mesh(geo, mat);
    };

    // Create drifting ash particles
    NHIPet.prototype._createAshParticles = function() {
        var THREE = global.THREE;
        var geo = new THREE.BufferGeometry();
        var count = 30;
        var positions = new Float32Array(count * 3);
        this.ashOffsets = [];
        for (var i = 0; i < count; i++) {
            positions[i * 3]     = (Math.random() - 0.5) * 2;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 2 + 0.5;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 2;
            this.ashOffsets.push({
                x: (Math.random() - 0.5) * 0.005,
                y: -Math.random() * 0.01 - 0.002,
                z: (Math.random() - 0.5) * 0.005,
            });
        }
        geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        var mat = new THREE.PointsMaterial({
            color: 0x8b4513,
            size: 0.08,
            transparent: true,
            opacity: 0.5,
            sizeAttenuation: false,
        });
        this.ashParticles = new THREE.Points(geo, mat);
        this.petGroup.add(this.ashParticles);
    };

    // ═══ Event bindings ═══
    NHIPet.prototype._bindEvents = function() {
        var self = this;
        this.container.addEventListener('mousemove', function(e) {
            var rect = self.container.getBoundingClientRect();
            self.mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            self.mouseY = -((e.clientY - rect.top) / rect.height) * 2 + 1;
            var dist = Math.sqrt(self.mouseX * self.mouseX + self.mouseY * self.mouseY);
            self.mouseNear = dist < 0.5;
            self.lastInteraction = Date.now();
            if (self.mood === 'sleepy' || self.mood === 'idle') {
                self._setMood('curious');
            }
        });
        this.container.addEventListener('click', function() {
            self._cycleMood();
        });
    };

    // ═══ Mood system ═══
    NHIPet.prototype._setMood = function(newMood) {
        var mood = MOODS[newMood];
        if (!mood) return;
        this.mood = newMood;
        this.moodTimer = Date.now();
        this._applyMood();
    };

    NHIPet.prototype._applyMood = function() {
        var mood = MOODS[this.mood];
        this.body.material.color.setHex(mood.color);
        for (var i = 0; i < this.eyes.length; i++) {
            this.eyes[i].mesh.material.color.setHex(mood.eyeColor);
        }
        for (var j = 0; j < this.runes.length; j++) {
            this.runes[j].material.color.setHex(mood.runeColor);
        }
        this.coreMat.color.setHex(mood.eyeColor);
    };

    NHIPet.prototype._cycleMood = function() {
        var order = ['idle', 'curious', 'happy', 'excited', 'sleepy'];
        var idx = order.indexOf(this.mood);
        if (idx === -1 || this.mood === 'hungry' || this.mood === 'sleepy') {
            idx = 0; // wake from sleep/hunger when petted
        } else {
            idx = (idx + 1) % order.length;
        }
        this._setMood(order[idx]);
        this.lastInteraction = Date.now();
    };

    // ═══ Animation loop ═══
    NHIPet.prototype._animate = function() {
        var self = this;
        requestAnimationFrame(function() { self._animate(); });
        self._update();
        self.renderer.render(self.scene, self.camera);
    };

    NHIPet.prototype._update = function() {
        var time = Date.now() * 0.001;
        var mood = MOODS[this.mood];

        // Float + gentle rotation
        this.petGroup.position.y = Math.sin(time * mood.floatSpeed * 0.5) * 0.05;
        this.petGroup.rotation.y = Math.sin(time * mood.floatSpeed * 0.2) * 0.1;

        // Body pulse
        var scale = 1 + Math.sin(time * mood.pulseSpeed) * 0.02;
        this.body.scale.set(scale, scale, scale);

        // Core orb pulse (NHI bio-luminescence)
        this.coreMat.opacity = 0.4 + Math.sin(time * mood.pulseSpeed * 1.5) * 0.3;

        // Eyes: blink + look toward mouse
        for (var i = 0; i < this.eyes.length; i++) {
            var eye = this.eyes[i];
            var blink = Math.abs(Math.sin(time * mood.pulseSpeed * 0.3 + eye.blinkPhase));
            var s = 1 - blink * 0.02 * (this.mood === 'sleepy' ? 0.8 : 0.3);
            eye.mesh.scale.set(s, s, s);

            if (this.mouseNear || this.mood === 'curious' || this.mood === 'happy' || this.mood === 'excited') {
                eye.mesh.position.x = eye.offset.x + this.mouseX * 0.1;
                eye.mesh.position.y = eye.offset.y + this.mouseY * 0.1;
            } else {
                eye.mesh.position.x = eye.mesh.position.x * 0.9 + eye.offset.x * 0.1;
                eye.mesh.position.y = eye.mesh.position.y * 0.9 + eye.offset.y * 0.1;
            }
        }

        // Tentacles sway
        for (var t = 0; t < this.tentacles.length; t++) {
            var wave = Math.sin(time * mood.floatSpeed * 0.8 + t * 1.5) * 0.15;
            this.tentacles[t].mesh.rotation.z = this.tentacles[t].baseAngle + Math.PI / 2 + wave;
        }

        // Antennae sway + glowing tips
        for (var a = 0; a < this.antennae.length; a++) {
            var item = this.antennae[a];
            item.mesh.rotation.z = Math.sin(time * mood.floatSpeed + a * 2) * 0.1 + (a === 0 ? 0.3 : -0.3);
            if (item.tip) {
                item.tip.material.opacity = 0.6 + Math.sin(time * mood.pulseSpeed * 2 + a) * 0.3;
            }
        }

        // Runes orbit slowly
        for (var r = 0; r < this.runes.length; r++) {
            var rune = this.runes[r];
            var rd = rune.userData.radius;
            rune.position.x = Math.cos(time * 0.2 + rune.userData.phase + r) * rd;
            rune.position.z = Math.sin(time * 0.2 + rune.userData.phase + r) * rd;
            rune.position.y = Math.sin(time * 0.3 + rune.userData.phase) * 0.3;
        }

        // Ash particles drift
        var pos = this.ashParticles.geometry.attributes.position.array;
        for (var i = 0; i < pos.length / 3; i++) {
            pos[i * 3]     += this.ashOffsets[i].x;
            pos[i * 3 + 1] += this.ashOffsets[i].y;
            pos[i * 3 + 2] += this.ashOffsets[i].z;
            if (pos[i * 3 + 1] < -1.5) {
                pos[i * 3]     = (Math.random() - 0.5) * 2;
                pos[i * 3 + 1] = 1.5;
                pos[i * 3 + 2] = (Math.random() - 0.5) * 2;
            }
        }
        this.ashParticles.geometry.attributes.position.needsUpdate = true;

        // Starvation: pet gets hungry if left alone
        var sinceInteract = Date.now() - this.lastInteraction;
        if (sinceInteract > this.starveThreshold && this.mood !== 'sleepy' && this.mood !== 'hungry') {
            this._setMood('hungry');
        } else if (sinceInteract > this.hungerThreshold && this.mood === 'idle') {
            this._setMood('sleepy');
        }
        // Auto-return to idle after excitement fades
        if ((this.mood === 'happy' || this.mood === 'excited') && sinceInteract > 5000) {
            this._setMood('idle');
        }
    };

    // ═══ Static API ═══
    NHIPet.MOODS = MOODS;

    // Factory method
    NHIPet.create = function(selector, options) {
        return new NHIPet(selector, options);
    };

    // Export to global
    global.NHIPet = NHIPet;
    global.NHI_DigitalPet = NHIPet;

})(typeof window !== 'undefined' ? window : this);
