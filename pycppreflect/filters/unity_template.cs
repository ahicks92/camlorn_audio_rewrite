using System;
using System.Collections;
using System.Runtime.InteropServices;
 
using UnityEngine;
public class ExamplePluginLoader { 
	// Unity editor does not unload dlls after load (well technically C# doesn't)
	// The following code will handle automatic unloading on Windows only.  This
	// first section would need to be modified for OSX manually.
	#if UNITY_EDITOR
		IntPtr? plugin_dll = null;
		
		static class NativeMethods
		{
			[DllImport("kernel32.dll")]
			public static extern IntPtr LoadLibrary(string dllToLoad);
	 
			[DllImport("kernel32.dll")]
			public static extern IntPtr GetProcAddress(IntPtr hModule, string procedureName);
	 
			[DllImport("kernel32.dll")]
			public static extern bool FreeLibrary(IntPtr hModule);
		}
	 
		/*	//Example
		[UnmanagedFunctionPointer(CallingConvention.Cdecl)]
		private delegate IntPtr Delegate_New();
		Delegate_New plugin_new;
		*/
$editor_import_attributes
	 
		void InitializeHooks(){
			
			plugin_dll = NativeMethods.LoadLibrary(@$plugin);
	 
			IntPtr pAddressOfFunctionToCall = null;
			
			/*	//example
			pAddressOfFunctionToCall = NativeMethods.GetProcAddress(plugin_dll.Value, "plugin_new");
			plugin_new = (Delegate_New)Marshal.GetDelegateForFunctionPointer(pAddressOfFunctionToCall,typeof(Delegate_New));
			*/
$editor_import_delegates
		}
		void CloseHooks(){
			if(plugin_dll == null){
				return;
			}
			bool result = NativeMethods.FreeLibrary(plugin_dll.Value);
			Console.WriteLine(result);
	 
			plugin_dll = null;
		}
	#elif UNITY_ANDROID
		//python generated platform specific dll imports
$android_import_attributes
		
		void InitializeHooks(){}
		void CloseHooks(){}
	#elif UNITY_STANDALONE_WIN
		//python generated platform specific dll imports
$windows_import_attributes
		
		void InitializeHooks(){}
		void CloseHooks(){}
	#else 
		//python generated platform specific dll imports
$undefined_import_attributes
		
		void InitializeHooks(){}
		void CloseHooks(){}
	#endif
	
	IntPtr plugin_handle_;
	public Plugin(){
		Close();
	}
	 
	/// <summary>
	/// Close this instance.
	/// </summary>
	public void Close(){
	 
		CloseHooks();
	}
	 
	/// <summary>
	/// Initialize this instance.
	/// </summary>
	public void Initialize(){
		InitializeHooks();    
	}
}