import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, Img, Audio } from 'remotion';

export const ReelComposition = ({ productData, audioUrl }: any) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Smooth Spring Entry for Product Card (Google Vids style)
  const cardSpring = spring({
    frame: frame - 40,
    fps,
    config: { damping: 12, stiffness: 90 }
  });

  const cardScale = interpolate(cardSpring, [0, 1], [0.6, 1]);
  const cardOpacity = interpolate(cardSpring, [0, 1], [0, 1]);

  return (
    <AbsoluteFill style={{ backgroundColor: '#0b0e14', fontFamily: 'Arial, sans-serif' }}>
      {audioUrl && <Audio src={audioUrl} />}

      {/* Background Soft Glow */}
      <div style={{
        position: 'absolute',
        width: 700,
        height: 700,
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(0,255,102,0.18) 0%, rgba(0,0,0,0) 70%)',
        top: '20%',
        left: '18%'
      }} />

      {/* Floating 3D Rounded Product Card */}
      {frame >= 40 && (
        <div style={{
          position: 'absolute',
          top: 320,
          left: 140,
          width: 800,
          height: 800,
          background: '#ffffff',
          borderRadius: 48,
          boxShadow: '0 30px 80px rgba(0,0,0,0.6)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          transform: `scale(${cardScale})`,
          opacity: cardOpacity
        }}>
          <Img 
            src={productData?.image_url || "https://m.media-amazon.com/images/I/61SSVxTSs3L._SL1500_.jpg"} 
            style={{ maxHeight: 680, maxWidth: 680, objectFit: 'contain' }} 
          />
        </div>
      )}

      {/* Glowing Deal Price Badge */}
      {frame >= 65 && (
        <div style={{
          position: 'absolute',
          top: 1180,
          width: '100%',
          textAlign: 'center',
          color: '#00FF66',
          fontSize: 72,
          fontWeight: 900,
          textShadow: '0 4px 20px rgba(0,0,0,0.9)'
        }}>
          DEAL: {productData?.deal_price || "₹999"}
        </div>
      )}

      {/* Clean Call To Action */}
      <div style={{
        position: 'absolute',
        bottom: 220,
        width: '100%',
        textAlign: 'center',
        color: '#FFFFFF',
        fontSize: 54,
        fontWeight: 'bold',
        letterSpacing: 2
      }}>
        COMMENT "{productData?.keyword || "DEAL"}" FOR LINK
      </div>
    </AbsoluteFill>
  );
};
