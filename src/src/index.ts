import { registerRoot, Composition } from 'remotion';
import { ReelComposition } from './ReelComposition';
import fs from 'fs';

const productData = fs.existsSync('./active_deal.json') 
  ? JSON.parse(fs.readFileSync('./active_deal.json', 'utf8'))
  : { deal_price: "₹999", keyword: "DEAL" };

export const RemotionRoot = () => {
  return (
    <Composition
      id="ReelComposition"
      component={ReelComposition}
      durationInFrames={30 * 20} // 20 seconds at 30 fps
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{
        productData: productData,
        audioUrl: 'audio_te.mp3'
      }}
    />
  );
};

registerRoot(RemotionRoot);
