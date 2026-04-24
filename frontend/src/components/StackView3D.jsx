import React, { useState, useEffect, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars, Text, Float, ContactShadows, Environment } from '@react-three/drei';
import { X, Box, Info, LayoutGrid } from 'lucide-react';

export default function StackView3D({ zoneName, terminal, onClose }) {
  const [containers, setContainers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchZoneContainers = async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8000/conteneurs?terminal=${terminal}&zone=${zoneName}`);
        const data = await res.json();
        setContainers(data);
      } catch (err) {
        console.error("Erreur 3D:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchZoneContainers();
  }, [zoneName, terminal]);

  return (
    <div className="fixed inset-0 z-[100] bg-slate-950/95 backdrop-blur-xl flex flex-col overflow-hidden animate-in fade-in zoom-in duration-500">
      {/* Header Overlay */}
      <div className="absolute top-0 left-0 right-0 p-8 z-50 flex items-center justify-between pointer-events-none">
        <div className="pointer-events-auto">
          <div className="flex items-center gap-4 mb-2">
            <div className="bg-[#FF8C00] p-3 rounded-2xl shadow-lg shadow-orange-500/20">
              <LayoutGrid size={24} className="text-white" />
            </div>
            <div>
              <h2 className="text-4xl font-black text-white tracking-tighter uppercase leading-none">
                Vue 3D Bloc {zoneName}
              </h2>
              <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mt-1">
                Visualisation Volumétrique • Terminal {terminal}
              </p>
            </div>
          </div>
          <div className="flex gap-4">
             <div className="bg-slate-900/80 border border-slate-800 px-4 py-2 rounded-xl text-[10px] font-black text-white uppercase tracking-widest backdrop-blur-md">
                {containers.length} Conteneurs Actifs
             </div>
             <div className="bg-slate-900/80 border border-slate-800 px-4 py-2 rounded-xl text-[10px] font-black text-emerald-400 uppercase tracking-widest backdrop-blur-md">
                LIFO Optimisé
             </div>
          </div>
        </div>

        <button 
          onClick={onClose}
          className="pointer-events-auto bg-white/5 hover:bg-red-500/20 border border-white/10 hover:border-red-500/50 p-4 rounded-3xl transition-all group"
        >
          <X className="text-white group-hover:scale-110 transition-transform" size={32} />
        </button>
      </div>

      {/* Canvas 3D */}
      <div className="flex-1 w-full relative">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-16 h-16 border-4 border-[#FF8C00] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <Canvas camera={{ position: [25, 25, 25], fov: 40 }} shadows>
            <Suspense fallback={null}>
              <Scene containers={containers} />
              <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
              <Environment preset="night" />
              <ContactShadows position={[0, -0.5, 0]} opacity={0.4} scale={40} blur={2.4} far={4.5} />
            </Suspense>
            <OrbitControls 
              minPolarAngle={0} 
              maxPolarAngle={Math.PI / 2.1} 
              autoRotate 
              autoRotateSpeed={0.5}
              makeDefault 
            />
          </Canvas>
        )}
      </div>

      {/* Footer Controls */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-4 bg-slate-900/50 border border-slate-800 p-2 rounded-3xl backdrop-blur-xl">
         <div className="flex items-center gap-2 px-6 py-3">
            <div className="w-3 h-3 rounded-full bg-blue-500" />
            <span className="text-[10px] font-black text-white uppercase">Normal</span>
         </div>
         <div className="flex items-center gap-2 px-6 py-3">
            <div className="w-3 h-3 rounded-full bg-[#FF8C00]" />
            <span className="text-[10px] font-black text-white uppercase">Frigo</span>
         </div>
         <div className="flex items-center gap-2 px-6 py-3">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-[10px] font-black text-white uppercase">Danger</span>
         </div>
      </div>
    </div>
  );
}

function Scene({ containers }) {
  // On regroupe les conteneurs par pile (Allee-Pile)
  const stacks = {};
  containers.forEach(c => {
    const key = `${c.allee}-${c.pile}`;
    if (!stacks[key]) stacks[key] = [];
    stacks[key].push(c);
  });

  // Trier par niveau Z pour être sûr de l'ordre d'empilement
  Object.keys(stacks).forEach(key => {
    stacks[key].sort((a, b) => (a.niveau_z || 0) - (b.niveau_z || 0));
  });

  return (
    <group position={[-5, 0, -5]}>
      {/* Sol tactique */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.51, 0]} receiveShadow>
        <planeGeometry args={[100, 100]} />
        <meshStandardMaterial color="#020617" opacity={0.5} transparent />
      </mesh>
      <gridHelper args={[100, 50, "#1e293b", "#0f172a"]} position={[0, -0.5, 0]} />

  // Rendu des piles
  {Object.entries(stacks).map(([key, stackContainers], idx) => {
    const parts = key.split('-');
    const allee = parseInt(parts[0]) || 0;
    const pileRaw = parts[1] || "0";
    
    // Normalisation intelligente pour eviter les positions geantes (ex: ZONE_C)
    let pileNum = parseInt(pileRaw);
    if (isNaN(pileNum)) {
      // Si c'est du texte (ex: ZONE_C), on utilise l'index de la pile dans la liste des piles uniques
      const uniquePiles = Object.keys(stacks).map(k => k.split('-')[1]);
      const distinctPiles = [...new Set(uniquePiles)].sort();
      pileNum = distinctPiles.indexOf(pileRaw);
    }

    // Positionnement visuel centre
    const posX = (allee % 12) * 3 - 15; // Centre sur X
    const posZ = (pileNum) * 4 - 10;     // Centre sur Z 

    return (
      <group key={key} position={[posX, 0, posZ]}>
        {stackContainers.map((container, zIdx) => (
          <ContainerBox 
            key={container.container_id} 
            container={container} 
            zIdx={zIdx} 
          />
        ))}
      </group>
    );
  })}
    </group>
  );
}

function ContainerBox({ container }) {
  const [hovered, setHovered] = useState(false);
  
  // Couleurs industrielles Marsa Maroc
  const spec = String(container.specialite || container.type || "NORMAL").toUpperCase().trim();
  
  let color = "#3b82f6"; // Bleu par defaut
  
  if (spec === "FRIGO") color = "#FF8C00"; // Orange Marsa
  else if (spec === "DANGER") color = "#ef4444"; // Rouge Alerte
  else if (spec === "OOG" || spec === "HORS_GABARIT" || spec === "HORS GABARIT") color = "#a855f7"; // Violet
  else if (spec === "CITERNE") color = "#06b6d4"; // Cyan

  const height = 1.1;
  const width = 2.4;
  const depth = 1.2;
  
  // Utilisation du VRAI niveau Z de la DB (ex: 1, 2, 3...)
  const zLevel = (container.niveau_z || 1);
  const posY = (zLevel - 1) * height + (height / 2);

  return (
    <mesh 
      position={[0, posY, 0]} 
      castShadow 
      receiveShadow
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <boxGeometry args={[width, height - 0.05, depth]} />
      <meshStandardMaterial 
        color={hovered ? "#ffffff" : color} 
        roughness={0.2}
        metalness={0.8}
        emissive={hovered ? color : "#000000"}
        emissiveIntensity={0.5}
      />
      {hovered && (
        <Float speed={5} rotationIntensity={0.5} floatIntensity={0.5}>
          <Text
            position={[0, 1.2, 0]}
            fontSize={0.3}
            color="white"
            anchorX="center"
            anchorY="middle"
            font="/fonts/Inter-Bold.woff"
          >
            {container.reference}
          </Text>
        </Float>
      )}
    </mesh>
  );
}
