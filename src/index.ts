import { registerRoot, Composition } from 'remotion';
import { ReelComposition } from './ReelComposition';

export const RemotionRoot = () => {
  return (
    <Composition
      id="ReelComposition"
      component={ReelComposition}
      durationInFrames={30 * 20}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{
        productData: { deal_price: "₹999", keyword: "DEAL" },
        audioUrl: 'audio_te.mp3'
      }}
    />
  );
};

registerRoot(RemotionRoot);
